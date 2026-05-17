import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.collection import CollectionItem
from app.models.catalog import SectionType, CatalogItem, Period, Country, Continent
from app.schemas.collection import CollectionItemCreate, CollectionItemOut, CollectionItemUpdate, CollectionTree, TreeNode
from app.routes.auth import current_user
from app.models.user import User

router = APIRouter(prefix="/collection", tags=["collection"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _load_opts():
    return selectinload(CollectionItem.catalog_item).selectinload(
        CatalogItem.period
    ).selectinload(Period.country).selectinload(Country.continent)

def _enrich(item: CollectionItem) -> dict:
    """Attach period/country/continent from catalog_item hierarchy."""
    d = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    d["catalog_item"] = item.catalog_item
    d["period"] = None
    d["country"] = None
    d["continent"] = None
    if item.catalog_item and item.catalog_item.period:
        d["period"] = item.catalog_item.period
        if item.catalog_item.period.country:
            d["country"] = item.catalog_item.period.country
            if item.catalog_item.period.country.continent:
                d["continent"] = item.catalog_item.period.country.continent
    return d

@router.get("", response_model=list[CollectionItemOut])
async def get_collection(
    section: SectionType | None = Query(None),
    continent_id: int | None = Query(None),
    country_id: int | None = Query(None),
    condition: str | None = Query(None),
    search: str | None = Query(None),
    item_type: str | None = Query(None),
    catalog_item_id: int | None = Query(None),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(CollectionItem)
        .where(CollectionItem.user_id == user.id)
        .options(_load_opts())
        .order_by(CollectionItem.added_at.desc())
    )
    if section:
        q = q.where(CollectionItem.section == section)
    if condition:
        q = q.where(CollectionItem.condition == condition)
    if item_type:
        q = q.where(CollectionItem.item_type == item_type)
    if catalog_item_id:
        q = q.where(CollectionItem.catalog_item_id == catalog_item_id)

    result = await db.execute(q)
    items = result.scalars().all()

    # Filter by continent/country/search in Python (after join loaded)
    filtered = []
    for item in items:
        if continent_id and (not item.catalog_item or not item.catalog_item.period or
                             not item.catalog_item.period.country or
                             item.catalog_item.period.country.continent_id != continent_id):
            if not item.custom_country:
                continue
        if country_id and (not item.catalog_item or not item.catalog_item.period or
                           item.catalog_item.period.country_id != country_id):
            continue
        if search:
            name = (item.catalog_item.name if item.catalog_item else item.custom_name) or ""
            if search.lower() not in name.lower():
                continue
        filtered.append(item)

    def _sort_key(item):
        year = item.catalog_item.year if item.catalog_item else item.custom_year
        denom = item.catalog_item.denomination if item.catalog_item else item.custom_denomination
        try:
            y = int(year) if year else 0
        except (ValueError, TypeError):
            y = 0
        try:
            d = float("".join(c for c in (denom or "") if c.isdigit() or c == ".").rstrip(".") or "0")
        except (ValueError, TypeError):
            d = 0.0
        return (-y, -d)

    filtered.sort(key=_sort_key)
    return [CollectionItemOut(**_enrich(i)) for i in filtered]

@router.get("/tree", response_model=CollectionTree)
async def get_tree(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CollectionItem)
        .where(CollectionItem.user_id == user.id)
        .options(_load_opts())
    )
    items = result.scalars().all()

    tree = CollectionTree(total=len(items))

    # section → continent → country → period
    for section_key in ["coins", "medals", "stamps", "banknotes"]:
        cont_map: dict[str, dict] = {}

        for item in items:
            if item.section.value != section_key:
                continue

            ci = item.catalog_item
            if ci and ci.period and ci.period.country:
                country = ci.period.country
                continent = country.continent
                cont_name = (continent.name_lv or continent.name) if continent else "Citi"
                cont_id = continent.id if continent else 0
                c_name = country.name_lv or country.name
                c_id = country.id
                c_code = country.code
                p_name = ci.period.name
                p_id = ci.period.id
                p_year_start = ci.period.year_start
                p_year_end = ci.period.year_end
            else:
                cont_name = "Citi"
                cont_id = 0
                c_name = item.custom_country or "Nezināma valsts"
                c_id = hash(c_name) & 0x7FFFFFFF
                c_code = None
                p_name = "Nezināms periods"
                p_id = hash(f"{c_name}-unknown") & 0x7FFFFFFF
                p_year_start = None
                p_year_end = None

            if cont_name not in cont_map:
                cont_map[cont_name] = {"id": cont_id, "count": 0, "countries": {}}
            cont_map[cont_name]["count"] += 1

            c_map = cont_map[cont_name]["countries"]
            if c_name not in c_map:
                c_map[c_name] = {"id": c_id, "code": c_code, "count": 0, "periods": {}}
            c_map[c_name]["count"] += 1

            p_map = c_map[c_name]["periods"]
            if p_name not in p_map:
                p_map[p_name] = {"id": p_id, "count": 0, "year_start": p_year_start, "year_end": p_year_end}
            p_map[p_name]["count"] += 1

        continent_nodes = []
        for cont_name, cont_data in cont_map.items():
            country_nodes = []
            for c_name, c_data in cont_data["countries"].items():
                period_nodes = []
                for p_name, p_data in c_data["periods"].items():
                    period_nodes.append(TreeNode(
                        id=p_data["id"],
                        name=p_name,
                        count=p_data["count"],
                        year_start=p_data["year_start"],
                        year_end=p_data["year_end"],
                    ))
                period_nodes.sort(key=lambda n: n.year_start or 0)
                country_nodes.append(TreeNode(
                    id=c_data["id"],
                    name=c_name,
                    code=c_data["code"],
                    count=c_data["count"],
                    children=period_nodes,
                ))
            country_nodes.sort(key=lambda n: n.name)
            continent_nodes.append(TreeNode(
                id=cont_data["id"],
                name=cont_name,
                count=cont_data["count"],
                children=country_nodes,
            ))
        continent_nodes.sort(key=lambda n: n.name)
        setattr(tree, section_key, continent_nodes)

    return tree

@router.get("/{item_id}", response_model=CollectionItemOut)
async def get_item(
    item_id: int,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CollectionItem)
        .where(CollectionItem.id == item_id, CollectionItem.user_id == user.id)
        .options(_load_opts())
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Nav atrasts")
    return CollectionItemOut(**_enrich(item))

@router.patch("/{item_id}", response_model=CollectionItemOut)
async def update_item(
    item_id: int,
    data: CollectionItemUpdate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CollectionItem)
        .where(CollectionItem.id == item_id, CollectionItem.user_id == user.id)
        .options(_load_opts())
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Nav atrasts")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    result2 = await db.execute(
        select(CollectionItem).where(CollectionItem.id == item_id).options(_load_opts())
    )
    item = result2.scalar_one()
    return CollectionItemOut(**_enrich(item))

@router.post("", response_model=CollectionItemOut)
async def add_to_collection(
    data: CollectionItemCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    item = CollectionItem(user_id=user.id, **data.model_dump())
    db.add(item)
    await db.commit()
    result = await db.execute(
        select(CollectionItem).where(CollectionItem.id == item.id).options(_load_opts())
    )
    item = result.scalar_one()
    return CollectionItemOut(**_enrich(item))

@router.post("/{item_id}/image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    side: str = Query("obverse", description="'obverse' vai 'reverse'"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CollectionItem).where(CollectionItem.id == item_id, CollectionItem.user_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Nav atrasts")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    url = f"/uploads/{filename}"
    if side == "reverse":
        item.user_image_reverse = url
    else:
        item.user_image = url
    await db.commit()
    return {"image_url": url, "side": side}

@router.delete("/{item_id}")
async def remove_from_collection(
    item_id: int,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CollectionItem).where(CollectionItem.id == item_id, CollectionItem.user_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Nav atrasts")
    await db.delete(item)
    await db.commit()
    return {"ok": True}
