from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, cast, Integer, Float, nulls_last, desc
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.catalog import Continent, Country, Period, CatalogItem, SectionType
from sqlalchemy.orm import selectinload as sl  # alias to avoid name clash below
from app.schemas.catalog import ContinentOut, CountryOut, PeriodOut, CatalogItemOut, RecognitionSave
from app.schemas.collection import CollectionTree, TreeNode
from app.routes.auth import current_user
from app.models.user import User

router = APIRouter(prefix="/catalog", tags=["catalog"])

# Bijušo PSRS republiku kodi (bez SU pašas) — periods ar "PSR" nosaukumā
# automātiski ietver arī SU kataloga priekšmetus
PSRS_REPUBLIC_CODES = {"RU", "UA", "BY", "LV", "LT", "EE", "MD", "GE", "AM", "AZ", "KZ", "UZ", "TM", "KG", "TJ"}

async def _expand_psrs_period_ids(period_id: int, db: AsyncSession) -> list[int]:
    """Ja periods pieder PSRS republikai, papildina ar SU periodu ID tiem pašiem sadaļas priekšmetiem."""
    row = await db.execute(
        select(Period, Country.code)
        .join(Country, Period.country_id == Country.id)
        .where(Period.id == period_id)
    )
    p = row.first()
    if not p:
        return [period_id]
    period_obj, c_code = p
    if c_code not in PSRS_REPUBLIC_CODES:
        return [period_id]
    if "PSR" not in (period_obj.name or "") and "PSRS" not in (period_obj.name or ""):
        return [period_id]
    su_r = await db.execute(
        select(Period.id)
        .join(Country, Period.country_id == Country.id)
        .where(Country.code == "SU", Period.section == period_obj.section)
    )
    su_ids = [r[0] for r in su_r.all()]
    return [period_id] + su_ids

@router.get("/continents", response_model=list[ContinentOut])
async def get_continents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Continent).order_by(Continent.name_lv))
    return result.scalars().all()

@router.get("/countries", response_model=list[CountryOut])
async def get_countries(
    continent_id: int | None = Query(None),
    is_extinct: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Country).order_by(Country.name_lv)
    if continent_id:
        q = q.where(Country.continent_id == continent_id)
    if is_extinct is not None:
        q = q.where(Country.is_extinct == is_extinct)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/periods", response_model=list[PeriodOut])
async def get_periods(
    country_id: int | None = Query(None),
    section: SectionType | None = Query(None),
    coin_category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Period).order_by(Period.year_start)
    if country_id:
        q = q.where(Period.country_id == country_id)
    if section:
        q = q.where(Period.section == section)
    if coin_category:
        q = q.where(Period.coin_category == coin_category)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/items", response_model=list[CatalogItemOut])
async def get_items(
    period_id: int | None = Query(None),
    country_id: int | None = Query(None),
    section: SectionType | None = Query(None),
    coin_category: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(CatalogItem).join(Period, CatalogItem.period_id == Period.id, isouter=True).where(CatalogItem.is_approved.is_(True))
    if period_id:
        ids = await _expand_psrs_period_ids(period_id, db)
        q = q.where(CatalogItem.period_id.in_(ids))
    if country_id:
        q = q.where(Period.country_id == country_id)
    if section:
        q = q.where(CatalogItem.section == section)
    if coin_category:
        q = q.where(CatalogItem.coin_category == coin_category)
    if search:
        q = q.where(CatalogItem.name.ilike(f"%{search}%"))
    q = q.order_by(
        nulls_last(Period.year_start),
        nulls_last(cast(CatalogItem.year, Integer)),
        nulls_last(cast(CatalogItem.denomination, Float)),
    )
    result = await db.execute(q.limit(500))
    items = result.scalars().all()

    # Bulk avg_price — viens vaicājums visiem priekšmetiem
    from app.models.collection import CollectionItem
    item_ids = [i.id for i in items]
    price_map: dict = {}
    if item_ids:
        pr = await db.execute(
            select(
                CollectionItem.catalog_item_id,
                func.avg(CollectionItem.purchase_price),
                func.count(CollectionItem.purchase_price),
            ).where(
                CollectionItem.catalog_item_id.in_(item_ids),
                CollectionItem.purchase_price.is_not(None),
            ).group_by(CollectionItem.catalog_item_id)
        )
        for cid, avg, cnt in pr.all():
            price_map[cid] = (avg, cnt)

    out = []
    for item in items:
        d = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        avg, cnt = price_map.get(item.id, (None, 0))
        d["avg_price"] = round(float(avg), 2) if avg is not None else None
        d["avg_price_count"] = cnt or 0
        out.append(d)
    return out

@router.get("/items/{item_id}/avg_price")
async def get_avg_price(item_id: int, db: AsyncSession = Depends(get_db)):
    """Vidējā pirkuma cena no visiem kolekcionāriem, kas norādījuši cenu."""
    from app.models.collection import CollectionItem
    r = await db.execute(
        select(
            func.avg(CollectionItem.purchase_price),
            func.count(CollectionItem.purchase_price),
        ).where(
            CollectionItem.catalog_item_id == item_id,
            CollectionItem.purchase_price.is_not(None),
        )
    )
    avg, count = r.one()
    return {
        "avg_price": round(float(avg), 2) if avg is not None else None,
        "count": count or 0,
    }


@router.get("/metal-price")
async def get_metal_price(metal: str = Query(..., description="'gold' vai 'silver'")):
    import httpx
    import asyncio
    metal_ticker = "GC%3DF" if metal == "gold" else "SI%3DF"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async def fetch(ticker):
        async with httpx.AsyncClient(timeout=8, verify=False) as c:
            r = await c.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                params={"interval": "1d", "range": "1d"},
                headers=headers,
            )
            return r.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]

    try:
        price_usd, eur_usd = await asyncio.gather(
            fetch(metal_ticker),
            fetch("EURUSD%3DX"),
        )
        return {
            "metal": metal,
            "price_usd_oz": round(float(price_usd), 4),
            "eur_usd_rate": round(float(eur_usd), 6),
        }
    except Exception:
        raise HTTPException(503, "Nevar iegūt metāla cenu")


@router.get("/items/{item_id}", response_model=CatalogItemOut)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CatalogItem).where(CatalogItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/tree", response_model=CollectionTree)
async def get_catalog_tree(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CatalogItem).where(CatalogItem.is_approved.is_(True)).options(
            selectinload(CatalogItem.period)
            .selectinload(Period.country)
            .selectinload(Country.continent)
        )
    )
    items = result.scalars().all()
    tree = CollectionTree(total=len(items))

    for section_key in ["coins", "medals", "stamps", "banknotes"]:
        # cont_name -> {id, code, count, countries: {c_name -> {id, code, count, periods: {p_name -> {id, count, cats: {}}}}}}
        cont_map: dict = {}

        for item in items:
            if item.section.value != section_key:
                continue
            if not (item.period and item.period.country):
                continue

            country   = item.period.country
            continent = country.continent

            cont_name = (continent.name_lv or continent.name) if continent else "Citi"
            cont_id   = continent.id if continent else 0
            cont_code = continent.code if continent else ""

            c_name = country.name_lv or country.name
            c_id   = country.id
            c_code = country.code

            p_name = item.period.name
            p_id   = item.period.id
            cat    = item.coin_category or "circulation"

            if cont_name not in cont_map:
                cont_map[cont_name] = {"id": cont_id, "code": cont_code, "count": 0, "countries": {}}
            cont_map[cont_name]["count"] += 1

            c_map = cont_map[cont_name]["countries"]
            if c_name not in c_map:
                c_map[c_name] = {"id": c_id, "code": c_code, "count": 0, "periods": {}}
            c_map[c_name]["count"] += 1

            p_map = c_map[c_name]["periods"]
            if p_name not in p_map:
                p_map[p_name] = {"id": p_id, "count": 0, "cats": {}}
            p_map[p_name]["count"] += 1

            if section_key == "coins":
                p_map[p_name]["cats"][cat] = p_map[p_name]["cats"].get(cat, 0) + 1

        continent_nodes = []
        for cont_name, cont_data in cont_map.items():
            country_nodes = []
            for c_name, c_data in cont_data["countries"].items():
                period_nodes = []
                for p_name, p_data in c_data["periods"].items():
                    cat_children = []
                    if section_key == "coins":
                        cat_children = [
                            TreeNode(id=hash(f"{p_data['id']}-{c}") & 0x7FFFFFFF, name=c, count=cnt)
                            for c, cnt in sorted(p_data["cats"].items())
                        ]
                    period_nodes.append(TreeNode(
                        id=p_data["id"], name=p_name, count=p_data["count"], children=cat_children,
                    ))
                country_nodes.append(TreeNode(
                    id=c_data["id"], name=c_name, code=c_data["code"],
                    count=c_data["count"], children=period_nodes,
                ))
            country_nodes.sort(key=lambda n: n.name)
            continent_nodes.append(TreeNode(
                id=cont_data["id"], name=cont_name, code=cont_data["code"],
                count=cont_data["count"], children=country_nodes,
            ))
        continent_nodes.sort(key=lambda n: n.name)
        setattr(tree, section_key, continent_nodes)

    return tree


@router.post("/from-recognition", response_model=CatalogItemOut)
async def create_from_recognition(
    data: RecognitionSave,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Izveido CatalogItem no AI atpazīšanas rezultāta, atrod pareizo periodu pēc valsts+gada."""

    # 1. Atrast valsti pēc angļu nosaukuma (precīzākā atbilstība vispirms)
    period = None
    country = None
    if data.country:
        # Meklē precīzu sakritību
        r = await db.execute(
            select(Country).where(Country.name.ilike(data.country))
        )
        country = r.scalars().first()

        # Ja nav precīzas, meklē daļēju sakritību
        if not country:
            r = await db.execute(
                select(Country).where(Country.name.ilike(f"%{data.country}%"))
            )
            country = r.scalars().first()

        if country:
            # 2. Atrast periodu pēc gada
            year_int = None
            if data.year:
                try:
                    year_int = int(str(data.year).strip()[:4])
                except ValueError:
                    pass

            if year_int:
                r2 = await db.execute(
                    select(Period).where(
                        Period.country_id == country.id,
                        Period.section == data.section,
                        or_(Period.year_start.is_(None), Period.year_start <= year_int),
                        or_(Period.year_end.is_(None), Period.year_end >= year_int),
                    ).order_by(Period.year_start.desc())
                )
                period = r2.scalars().first()

            if not period:
                # Fallback — pēdējais periods šai valstij/sadaļai
                r3 = await db.execute(
                    select(Period).where(
                        Period.country_id == country.id,
                        Period.section == data.section,
                    ).order_by(Period.year_start.desc())
                )
                period = r3.scalars().first()

    if not period:
        country_info = f"valsts='{data.country}'" + (f", gads={data.year}" if data.year else "")
        db_country = f" (DB atrasta: '{country.name}')" if country else " (valsts DB nav atrasta)"
        raise HTTPException(
            status_code=422,
            detail=f"Nevar atrast periodu: {country_info}{db_country}. Sadaļa: {data.section}."
        )

    coin_cat = data.coin_category or "circulation"

    # 3. Meklē esošu ierakstu — ja jau ir katalogā (apstiprināts vai ne), pievieno kolekciju tam
    dup_conds = [
        CatalogItem.period_id == period.id,
        CatalogItem.section == data.section,
        CatalogItem.coin_category == coin_cat,
    ]
    if data.year:
        dup_conds.append(CatalogItem.year == data.year)
    if data.denomination:
        dup_conds.append(CatalogItem.denomination == data.denomination)
    elif data.catalog_number:
        dup_conds.append(CatalogItem.catalog_number == data.catalog_number)

    if data.year or data.denomination or data.catalog_number:
        # Prioritāte: vispirms neapstiprināts (pending), tad apstiprināts
        dup_r = await db.execute(
            select(CatalogItem).where(*dup_conds).order_by(CatalogItem.is_approved.asc())
        )
        existing = dup_r.scalars().first()
        if existing:
            return existing

    # 4. Izveidot CatalogItem
    item = CatalogItem(
        section=data.section,
        period_id=period.id,
        name=data.name or "Nezināms",
        year=data.year,
        description=data.description,
        obverse_description=data.obverse_description,
        reverse_description=data.reverse_description,
        denomination=data.denomination,
        material=data.material,
        diameter_mm=data.diameter_mm,
        weight_g=data.weight_g,
        mint=data.mint,
        mintage=data.mintage,
        catalog_number=data.catalog_number,
        perforation=data.perforation,
        color=data.color,
        coin_category=coin_cat,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
