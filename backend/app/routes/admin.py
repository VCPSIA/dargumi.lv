import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, Integer, Float, nulls_last, desc
from pydantic import BaseModel
from app.database import get_db
from app.models.catalog import CatalogItem, Continent, Country, Period, SectionType
from app.models.user import User
from app.schemas.catalog import CatalogItemOut, ContinentOut, CountryOut, PeriodOut
from app.routes.auth import current_user

router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = "uploads"

async def require_admin(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Nepieciešamas admina tiesības")
    return user


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class CatalogItemUpdate(BaseModel):
    name: str | None = None
    year: str | None = None
    description: str | None = None
    denomination: str | None = None
    material: str | None = None
    diameter_mm: str | None = None
    weight_g: str | None = None
    mint: str | None = None
    mintage: str | None = None
    catalog_number: str | None = None
    obverse_description: str | None = None
    reverse_description: str | None = None
    perforation: str | None = None
    color: str | None = None
    coin_category: str | None = None


class ContinentCreate(BaseModel):
    name: str
    name_lv: str
    code: str

class ContinentUpdate(BaseModel):
    name: str | None = None
    name_lv: str | None = None
    code: str | None = None


class CountryCreate(BaseModel):
    name: str
    name_lv: str
    code: str
    continent_id: int
    is_extinct: bool = False

class CountryUpdate(BaseModel):
    name: str | None = None
    name_lv: str | None = None
    code: str | None = None
    continent_id: int | None = None
    is_extinct: bool | None = None


class PeriodCreate(BaseModel):
    name: str
    year_start: int | None = None
    year_end: int | None = None
    country_id: int
    section: SectionType

class PeriodUpdate(BaseModel):
    name: str | None = None
    year_start: int | None = None
    year_end: int | None = None
    section: SectionType | None = None
    country_id: int | None = None


class CatalogItemCreate(BaseModel):
    period_id: int
    section: SectionType
    coin_category: str = "circulation"
    name: str
    year: str | None = None
    denomination: str | None = None
    material: str | None = None
    diameter_mm: str | None = None
    weight_g: str | None = None
    mint: str | None = None
    mintage: str | None = None
    catalog_number: str | None = None
    description: str | None = None
    obverse_description: str | None = None
    reverse_description: str | None = None
    perforation: str | None = None
    color: str | None = None


# ── Catalog list / create ──────────────────────────────────────────────────────

@router.get("/catalog", response_model=list[CatalogItemOut])
async def admin_list_catalog(
    search: str | None = Query(None),
    section: SectionType | None = Query(None),
    period_id: int | None = Query(None),
    country_id: int | None = Query(None),
    coin_category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(CatalogItem).where(CatalogItem.is_approved.is_(True))
    if period_id:
        q = q.where(CatalogItem.period_id == period_id)
    elif country_id:
        period_ids_q = select(Period.id).where(Period.country_id == country_id)
        q = q.where(CatalogItem.period_id.in_(period_ids_q))
    if coin_category:
        q = q.where(CatalogItem.coin_category == coin_category)
    if search:
        q = q.where(CatalogItem.name.ilike(f"%{search}%"))
    q = q.order_by(
        nulls_last(desc(cast(CatalogItem.year, Integer))),
        nulls_last(desc(cast(CatalogItem.denomination, Float))),
    ).limit(500)
    r = await db.execute(q)
    return r.scalars().all()


@router.post("/catalog", response_model=CatalogItemOut)
async def admin_create_catalog_item(
    data: CatalogItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    period = await db.get(Period, data.period_id)
    if not period:
        raise HTTPException(404, "Periods nav atrasts")

    # Pārbauda duplikātus: period + year + denomination + coin_category
    dup_conds = [
        CatalogItem.period_id == data.period_id,
        CatalogItem.section == data.section,
        CatalogItem.coin_category == data.coin_category,
    ]
    if data.year:
        dup_conds.append(CatalogItem.year == data.year)
    if data.denomination:
        dup_conds.append(CatalogItem.denomination == data.denomination)
    elif data.catalog_number:
        dup_conds.append(CatalogItem.catalog_number == data.catalog_number)

    if data.year or data.denomination or data.catalog_number:
        dup_r = await db.execute(select(CatalogItem).where(*dup_conds))
        existing = dup_r.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ieraksts jau eksistē (ID: {existing.id}): {existing.name}"
            )

    item = CatalogItem(
        period_id=data.period_id,
        section=data.section,
        coin_category=data.coin_category,
        name=data.name,
        year=data.year,
        denomination=data.denomination,
        material=data.material,
        diameter_mm=data.diameter_mm,
        weight_g=data.weight_g,
        mint=data.mint,
        mintage=data.mintage,
        catalog_number=data.catalog_number,
        description=data.description,
        obverse_description=data.obverse_description,
        reverse_description=data.reverse_description,
        perforation=data.perforation,
        color=data.color,
        admin_edited=True,
        is_approved=True,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# ── Catalog item detail / edit / image ────────────────────────────────────────

@router.get("/catalog/{item_id}", response_model=CatalogItemOut)
async def admin_get_catalog_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    r = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Nav atrasts")
    return item


@router.patch("/catalog/{item_id}", response_model=CatalogItemOut)
async def admin_edit_catalog(
    item_id: int,
    data: CatalogItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    r = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Nav atrasts")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    item.admin_edited = True
    await db.commit()
    await db.refresh(item)
    return item


@router.post("/catalog/{item_id}/image", response_model=CatalogItemOut)
async def admin_upload_image(
    item_id: int,
    file: UploadFile = File(...),
    side: str = Query("obverse", description="'obverse' vai 'reverse'"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    r = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Nav atrasts")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"cat_{item_id}_{side}_{uuid.uuid4().hex[:8]}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    url = f"/uploads/{filename}"
    if side == "reverse":
        item.image_url_reverse = url
    else:
        item.image_url = url
    item.admin_edited = True
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/catalog/{item_id}")
async def admin_delete_catalog_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    from app.models.collection import CollectionItem
    r = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Nav atrasts")

    # Iegūst valsts nosaukumu caur periodu
    country_name = None
    if item.period_id:
        period = await db.get(Period, item.period_id)
        if period:
            country = await db.get(Country, period.country_id)
            if country:
                country_name = country.name_lv or country.name

    # Saglabā kataloga datus kolekcijas ierakstos pirms dzēšanas
    full_desc = _full_description(item)
    ci_r = await db.execute(select(CollectionItem).where(CollectionItem.catalog_item_id == item_id))
    for ci in ci_r.scalars().all():
        ci.custom_name = ci.custom_name or item.name
        ci.custom_year = ci.custom_year or item.year
        ci.custom_denomination = ci.custom_denomination or item.denomination
        ci.custom_material = ci.custom_material or item.material
        ci.custom_country = ci.custom_country or country_name
        ci.custom_description = ci.custom_description or full_desc
        ci.catalog_item_id = None

    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.delete("/catalog/{item_id}/image")
async def admin_delete_image(
    item_id: int,
    side: str = Query("obverse"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    r = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Nav atrasts")
    if side == "reverse":
        item.image_url_reverse = None
    else:
        item.image_url = None
    await db.commit()
    return {"ok": True}


# ── Continents ─────────────────────────────────────────────────────────────────

@router.post("/continents", response_model=ContinentOut)
async def admin_create_continent(
    data: ContinentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = await db.execute(select(Continent).where(Continent.code == data.code.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Kontinents ar kodu '{data.code}' jau eksistē")
    obj = Continent(name=data.name, name_lv=data.name_lv, code=data.code.upper())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Countries ──────────────────────────────────────────────────────────────────

@router.post("/countries", response_model=CountryOut)
async def admin_create_country(
    data: CountryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    continent = await db.get(Continent, data.continent_id)
    if not continent:
        raise HTTPException(404, "Kontinents nav atrasts")
    obj = Country(
        name=data.name, name_lv=data.name_lv,
        code=data.code.upper(), continent_id=data.continent_id,
        is_extinct=data.is_extinct,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Periods ────────────────────────────────────────────────────────────────────

@router.post("/periods", response_model=PeriodOut)
async def admin_create_period(
    data: PeriodCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    country = await db.get(Country, data.country_id)
    if not country:
        raise HTTPException(404, "Valsts nav atrasta")
    obj = Period(
        name=data.name,
        year_start=data.year_start,
        year_end=data.year_end,
        country_id=data.country_id,
        section=data.section,
        coin_category="circulation",
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Structure GET lists ────────────────────────────────────────────────────────

@router.get("/continents", response_model=list[ContinentOut])
async def admin_list_continents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    r = await db.execute(select(Continent).order_by(Continent.name_lv))
    return r.scalars().all()


# ── Pending submissions ────────────────────────────────────────────────────────

from app.models.collection import CollectionItem
from app.models.user import User as UserModel

def _full_description(item: CatalogItem) -> str | None:
    parts = [
        item.description,
        f"Priekšpuse: {item.obverse_description}" if item.obverse_description else None,
        f"Aizmugure: {item.reverse_description}" if item.reverse_description else None,
    ]
    result = "\n\n".join(p for p in parts if p)
    return result or None

@router.get("/pending")
async def admin_pending(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(CollectionItem).where(
        CollectionItem.catalog_item_id == None,
        CollectionItem.catalog_dismissed != 1,
    ).order_by(CollectionItem.added_at.desc())
    r = await db.execute(q)
    items = r.scalars().all()
    result = []
    for item in items:
        user = await db.get(UserModel, item.user_id)
        result.append({
            "id": item.id,
            "username": user.username if user else "?",
            "section": item.section,
            "custom_name": item.custom_name,
            "custom_year": item.custom_year,
            "custom_denomination": item.custom_denomination,
            "custom_country": item.custom_country,
            "custom_material": item.custom_material,
            "custom_description": item.custom_description,
            "user_image": item.user_image,
            "user_image_reverse": item.user_image_reverse,
            "coin_category": item.coin_category,
            "added_at": item.added_at.isoformat() if item.added_at else None,
        })
    return result


from sqlalchemy import or_

async def _find_or_create_period(ci: CollectionItem, db: AsyncSession) -> Period:
    country_name = (ci.custom_country or "Nezināma").strip()
    section = ci.section
    year = int(ci.custom_year) if ci.custom_year and ci.custom_year.isdigit() else 0

    # 1. Meklē valsti (pēc nosaukuma vai name_lv)
    r = await db.execute(
        select(Country).where(or_(
            Country.name.ilike(f"%{country_name}%"),
            Country.name_lv.ilike(f"%{country_name}%"),
        ))
    )
    country = r.scalars().first()

    if not country:
        # Atrod vai izveido kontinentu "Citi"
        r2 = await db.execute(select(Continent).where(Continent.code == "OTH"))
        continent = r2.scalar_one_or_none()
        if not continent:
            continent = Continent(name="Other", name_lv="Citi", code="OTH")
            db.add(continent)
            await db.flush()
        code = country_name[:3].upper().replace(" ", "")
        country = Country(name=country_name, name_lv=country_name, code=code, continent_id=continent.id)
        db.add(country)
        await db.flush()

    # 2. Meklē piemērotu periodu (pēc gadu diapazona)
    r = await db.execute(
        select(Period).where(
            Period.country_id == country.id,
            Period.section == section,
        )
    )
    periods = r.scalars().all()

    period = None
    if year:
        for p in periods:
            start_ok = p.year_start is None or p.year_start <= year
            end_ok = p.year_end is None or p.year_end >= year
            if start_ok and end_ok:
                period = p
                break
    if not period and periods:
        period = periods[0]

    if not period:
        period = Period(
            name=country_name,
            country_id=country.id,
            section=section,
            coin_category="circulation",
        )
        db.add(period)
        await db.flush()

    return period


@router.post("/pending/{item_id}/approve")
async def admin_approve_pending(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    ci = await db.get(CollectionItem, item_id)
    if not ci:
        raise HTTPException(404, "Nav atrasts")
    if ci.catalog_item_id:
        raise HTTPException(400, "Jau saistīts ar katalogu")

    period = await _find_or_create_period(ci, db)
    name = ci.custom_name or f"{ci.custom_denomination or ''} {ci.custom_year or ''}".strip() or "Bez nosaukuma"
    catalog_item = CatalogItem(
        period_id=period.id,
        section=ci.section,
        coin_category=ci.coin_category or "circulation",
        name=name,
        year=ci.custom_year,
        denomination=ci.custom_denomination,
        material=ci.custom_material,
        description=ci.custom_description,
        image_url=ci.user_image,
        image_url_reverse=ci.user_image_reverse,
        admin_edited=True,
        is_approved=True,
    )
    db.add(catalog_item)
    await db.flush()
    ci.catalog_item_id = catalog_item.id
    await db.commit()
    return {"id": catalog_item.id, "name": catalog_item.name}


@router.get("/pending-catalog")
async def admin_pending_catalog(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Kataloga ieraksti, kas gaida apstiprināšanu (izveidoti lietotāju AI atpazīšanā)."""
    from app.models.collection import CollectionItem
    q = select(CatalogItem).where(CatalogItem.is_approved.is_(False)).order_by(CatalogItem.id.desc())
    r = await db.execute(q)
    items = r.scalars().all()
    result = []
    for item in items:
        # Atrod lietotāja kolekcijas ierakstu, kas saistīts
        ci_r = await db.execute(
            select(CollectionItem).where(CollectionItem.catalog_item_id == item.id).limit(1)
        )
        ci = ci_r.scalar_one_or_none()
        user = await db.get(UserModel, ci.user_id) if ci else None
        result.append({
            "id": item.id,
            "name": item.name,
            "year": item.year,
            "denomination": item.denomination,
            "material": item.material,
            "section": item.section,
            "coin_category": item.coin_category,
            "image_url": ci.user_image if ci else None,
            "image_url_reverse": ci.user_image_reverse if ci else None,
            "username": user.username if user else "?",
        })
    return result


@router.post("/pending-catalog/{item_id}/approve")
async def admin_approve_pending_catalog(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = await db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Nav atrasts")
    item.is_approved = True
    item.admin_edited = True
    await db.commit()
    return {"id": item.id, "name": item.name}


@router.delete("/pending-catalog/{item_id}")
async def admin_reject_pending_catalog(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    from app.models.collection import CollectionItem
    item = await db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Nav atrasts")

    country_name = None
    if item.period_id:
        period = await db.get(Period, item.period_id)
        if period:
            country = await db.get(Country, period.country_id)
            if country:
                country_name = country.name_lv or country.name

    full_desc = _full_description(item)
    ci_r = await db.execute(select(CollectionItem).where(CollectionItem.catalog_item_id == item_id))
    for ci in ci_r.scalars().all():
        ci.custom_name = ci.custom_name or item.name
        ci.custom_year = ci.custom_year or item.year
        ci.custom_denomination = ci.custom_denomination or item.denomination
        ci.custom_material = ci.custom_material or item.material
        ci.custom_country = ci.custom_country or country_name
        ci.custom_description = ci.custom_description or full_desc
        ci.catalog_item_id = None
        ci.catalog_dismissed = 1
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.delete("/pending/{item_id}")
async def admin_dismiss_pending(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    ci = await db.get(CollectionItem, item_id)
    if not ci:
        raise HTTPException(404, "Nav atrasts")
    ci.catalog_dismissed = 1
    await db.commit()
    return {"ok": True}


@router.get("/countries", response_model=list[CountryOut])
async def admin_list_countries(
    continent_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(Country)
    if continent_id:
        q = q.where(Country.continent_id == continent_id)
    r = await db.execute(q.order_by(Country.name_lv))
    return r.scalars().all()


@router.get("/periods", response_model=list[PeriodOut])
async def admin_list_periods(
    country_id: int | None = Query(None),
    section: SectionType | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(Period)
    if country_id:
        q = q.where(Period.country_id == country_id)
    if section:
        q = q.where(Period.section == section)
    r = await db.execute(q.order_by(Period.year_start, Period.name))
    return r.scalars().all()


# ── Structure PATCH / DELETE ───────────────────────────────────────────────────

@router.patch("/continents/{cont_id}", response_model=ContinentOut)
async def admin_edit_continent(
    cont_id: int,
    data: ContinentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Continent, cont_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    for field, val in data.model_dump(exclude_none=True).items():
        if field == "code":
            val = val.upper()
        setattr(obj, field, val)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/continents/{cont_id}")
async def admin_delete_continent(
    cont_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Continent, cont_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    r = await db.execute(select(Country).where(Country.continent_id == cont_id).limit(1))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Nevar dzēst — ir saistītas valstis")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}


@router.patch("/countries/{country_id}", response_model=CountryOut)
async def admin_edit_country(
    country_id: int,
    data: CountryUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Country, country_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    for field, val in data.model_dump(exclude_none=True).items():
        if field == "code":
            val = val.upper()
        setattr(obj, field, val)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/countries/{country_id}")
async def admin_delete_country(
    country_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Country, country_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    r = await db.execute(select(Period).where(Period.country_id == country_id).limit(1))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Nevar dzēst — ir saistīti periodi")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}


@router.patch("/periods/{period_id}", response_model=PeriodOut)
async def admin_edit_period(
    period_id: int,
    data: PeriodUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Period, period_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(obj, field, val)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/periods/{period_id}")
async def admin_delete_period(
    period_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    obj = await db.get(Period, period_id)
    if not obj:
        raise HTTPException(404, "Nav atrasts")
    r = await db.execute(select(CatalogItem).where(CatalogItem.period_id == period_id).limit(1))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Nevar dzēst — ir saistīti kataloga ieraksti")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}
