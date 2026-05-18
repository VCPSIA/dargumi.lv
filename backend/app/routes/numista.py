import os
import uuid
import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.models.catalog import CatalogItem, Period, Country, Continent, SectionType
from app.models.user import User
from app.routes.auth import current_user
from app.config import settings

router = APIRouter(prefix="/admin/numista", tags=["numista"])
NUMISTA_BASE = "https://api.numista.com/api/v3"
UPLOAD_DIR = "uploads"


async def require_admin(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Nepieciešamas admina tiesības")
    return user


def _check_key():
    if not settings.numista_api_key:
        raise HTTPException(400, "NUMISTA_API_KEY nav konfigurēts .env failā")


@router.get("/search")
async def numista_search(
    q: str,
    category: str = Query("coin"),
    lang: str = Query("en"),
    _: User = Depends(require_admin),
):
    _check_key()
    async with httpx.AsyncClient(timeout=20, verify=False) as client:
        resp = await client.get(
            f"{NUMISTA_BASE}/types",
            params={"q": q, "category": category, "lang": lang, "count": 30, "page": 0},
            headers={"Numista-API-Key": settings.numista_api_key},
        )
        if resp.status_code == 401:
            raise HTTPException(401, "Numista API atslēga nav derīga")
        resp.raise_for_status()
    return resp.json()


@router.get("/type/{numista_id}")
async def numista_type_detail(
    numista_id: str,
    lang: str = Query("en"),
    _: User = Depends(require_admin),
):
    _check_key()
    async with httpx.AsyncClient(timeout=20, verify=False) as client:
        resp = await client.get(
            f"{NUMISTA_BASE}/types/{numista_id}",
            params={"lang": lang},
            headers={"Numista-API-Key": settings.numista_api_key},
        )
        resp.raise_for_status()
    return resp.json()


class NumistaImportBody(BaseModel):
    numista_id: str


async def _auto_period(db: AsyncSession, country_name: str, section: SectionType, year: int | None) -> Period:
    r = await db.execute(
        select(Country).where(or_(
            Country.name.ilike(f"%{country_name}%"),
            Country.name_lv.ilike(f"%{country_name}%"),
        ))
    )
    country = r.scalars().first()

    if not country:
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

    r = await db.execute(select(Period).where(Period.country_id == country.id, Period.section == section))
    periods = r.scalars().all()

    period = None
    if year:
        for p in periods:
            if (p.year_start is None or p.year_start <= year) and (p.year_end is None or p.year_end >= year):
                period = p
                break
    if not period and periods:
        period = periods[0]
    if not period:
        period = Period(name=country_name, country_id=country.id, section=section, coin_category="circulation")
        db.add(period)
        await db.flush()

    return period


def _extract_names(arr) -> list[str]:
    """Atbalsta gan ['Name'] gan [{'name': 'Name'}] formātus."""
    names = []
    for item in (arr or []):
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            n = item.get("name") or item.get("first_name", "") + " " + item.get("last_name", "")
            n = n.strip()
            if n:
                names.append(n)
    return names


def _side_desc(side: dict) -> str | None:
    parts = []
    if side.get("description"):
        parts.append(side["description"])
    if side.get("lettering"):
        leg = side["lettering"]
        trans = side.get("lettering_translation")
        parts.append("Leģenda: " + leg + (f" ({trans})" if trans else ""))
    return "\n".join(parts) or None


async def _fetch_mintage(numista_id: str, api_key: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=15, verify=False) as c:
            r = await c.get(
                f"{NUMISTA_BASE}/types/{numista_id}/issues",
                headers={"Numista-API-Key": api_key},
            )
            if r.status_code != 200:
                return None
        data = r.json()
        issues = data.get("issues") or []
        total = 0
        has_any = False
        for issue in issues:
            m = issue.get("mintage")
            if m and str(m).isdigit():
                total += int(m)
                has_any = True
        if not has_any:
            return None
        # Formatē ar tukšuma separatoriem
        return f"{total:,}".replace(",", " ")
    except Exception:
        return None


async def _fetch_metal_price(metal: str) -> str | None:
    """Iegūst zelta vai sudraba cenu USD/oz no Yahoo Finance."""
    ticker = "GC%3DF" if metal == "gold" else "SI%3DF"
    try:
        async with httpx.AsyncClient(timeout=10, verify=False) as c:
            r = await c.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                params={"interval": "1d", "range": "1d"},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
            )
            if r.status_code != 200:
                return None
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        metal_lv = "zelta" if metal == "gold" else "sudraba"
        return f"Pašreizējā {metal_lv} cena: ${price:.2f}/oz (importa brīdī)"
    except Exception:
        return None


@router.post("/import")
async def numista_import(
    body: NumistaImportBody,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    _check_key()

    dup = await db.execute(select(CatalogItem).where(CatalogItem.numista_id == body.numista_id))
    if dup.scalar_one_or_none():
        raise HTTPException(409, f"Monēta ar Numista ID {body.numista_id} jau importēta")

    async with httpx.AsyncClient(timeout=20, verify=False) as client:
        resp = await client.get(
            f"{NUMISTA_BASE}/types/{body.numista_id}",
            params={"lang": "en"},
            headers={"Numista-API-Key": settings.numista_api_key},
        )
        resp.raise_for_status()
    ndata = resp.json()

    _section_map = {"coin": "coins", "banknote": "banknotes", "stamp": "stamps", "exonumia": "medals"}
    section = SectionType(_section_map.get(ndata.get("category", "coin"), "coins"))

    issuer = ndata.get("issuer") or {}
    country_name = issuer.get("name") or "Unknown"
    year_for_period = ndata.get("min_year") or ndata.get("max_year")
    period = await _auto_period(db, country_name, section, year_for_period)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    referer = f"https://en.numista.com/catalogue/pieces{body.numista_id}.html"

    async def download_img(url: str | None, label: str) -> str | None:
        if not url:
            return None
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, verify=False) as c:
            r = await c.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": referer,
            })
            r.raise_for_status()
        ct = r.headers.get("content-type", "").lower()
        ext = "webp" if "webp" in ct else ("png" if "png" in ct else "jpg")
        fname = f"numista_{body.numista_id}_{label}_{uuid.uuid4().hex[:6]}.{ext}"
        with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
            f.write(r.content)
        return f"/uploads/{fname}"

    obv = ndata.get("obverse") or {}
    rev = ndata.get("reverse") or {}
    local_obv = await download_img(obv.get("picture"), "obv")
    local_rev = await download_img(rev.get("picture"), "rev")

    # Gads
    min_y = ndata.get("min_year")
    max_y = ndata.get("max_year")
    if min_y and max_y and min_y != max_y:
        year_str = f"{min_y}–{max_y}"
    elif min_y:
        year_str = str(min_y)
    else:
        year_str = None

    # Materiāls, svars, diametrs
    composition = ndata.get("composition") or {}
    material = composition.get("text") if isinstance(composition, dict) else None
    weight = ndata.get("weight")
    diameter = ndata.get("size")

    # Nominālvērtība
    value = ndata.get("value") or {}
    denomination = value.get("text") if isinstance(value, dict) else (str(value) if value else None)

    # KM kataloga numurs
    catalog_number = None
    for ref in (ndata.get("references") or []):
        cat = ref.get("catalogue") or {}
        if cat.get("code", "").upper() == "KM":
            catalog_number = f"KM#{ref.get('number', '')}"
            break
    if not catalog_number and ndata.get("references"):
        ref = ndata["references"][0]
        cat = ref.get("catalogue") or {}
        catalog_number = f"{cat.get('code', '')}#{ref.get('number', '')}"

    # Kaltuve no mints masīva
    mints_list = _extract_names(ndata.get("mints"))
    mint = ", ".join(mints_list) if mints_list else (country_name or None)

    # Tirāža no /issues
    mintage_str = await _fetch_mintage(body.numista_id, settings.numista_api_key)

    # Mākslinieks un gravieris (no abām pusēm apvienoti)
    all_designers = _extract_names(obv.get("designers")) + _extract_names(rev.get("designers"))
    seen = set()
    unique_designers = [x for x in all_designers if not (x in seen or seen.add(x))]
    designer_str = ", ".join(unique_designers) or None

    all_engravers = _extract_names(obv.get("engravers")) + _extract_names(rev.get("engravers"))
    seen2 = set()
    unique_engravers = [x for x in all_engravers if not (x in seen2 or seen2.add(x))]
    engraver_str = ", ".join(unique_engravers) or None

    # Priekšpuses un aizmugures apraksti
    obverse_description = _side_desc(obv)
    reverse_description = _side_desc(rev)

    # ── Tulkošanas vārdnīcas ────────────────────────────────────────
    _SHAPE_LV = {
        "round": "apaļa", "square": "kvadrātveida", "rectangular": "taisnstūrveida",
        "hexagonal": "sešstūraina", "octagonal": "astoņstūraina",
        "dodecagonal": "divpadsmitastūraina", "heptagonal": "septiņstūraina",
        "pentagonal": "piecstūraina", "oval": "ovāla", "irregular": "neregulāra",
        "triangular": "trīsstūraina", "heart": "sirdsveida", "flower": "ziedsveida",
        "scalloped": "viļņainas malas", "bimetallic": "divmetālu",
        "wavy": "viļņaina", "multisided": "daudzstūraina",
    }
    _EDGE_LV = {
        "plain": "gluda", "smooth": "gluda", "reeded": "rievota", "milled": "rievota",
        "lettered": "ar uzrakstu", "security": "drošības",
        "intermittently reeded": "daļēji rievota", "grooved": "ar rievām",
        "segmented reeding": "segmentēta rievošana", "grained": "granulēta",
        "ornamented": "ornamentēta", "decorated": "dekorēta", "serrated": "zobaina",
    }
    _ORIENT_LV = {
        "coin": "monētas apgrieziens", "medal": "medaļas apgrieziens",
        "coin rotation": "monētas apgrieziens", "medal rotation": "medaļas apgrieziens",
        "varies": "dažāds",
    }
    _TYPE_LV = {
        "circulating coin": "Apgrozības monēta",
        "commemorative coin": "Piemiņas monēta",
        "non-circulating coin": "Kolekcionāru monēta",
        "collector coin": "Kolekcionāru monēta",
        "bullion coin": "Dārgmetālu monēta",
        "bullion": "Dārgmetālu monēta",
        "proof coin": "Spoguļspīdums (Proof)",
        "pattern": "Paraugs / Próba",
        "token": "Žetons",
        "medal": "Medaļa",
    }

    def _tlv(val: str | None, d: dict) -> str | None:
        if not val:
            return None
        return d.get(val.lower().strip(), val)

    # ── Vispārīgs apraksts ──────────────────────────────────────────
    desc_parts = []
    obj_type_raw = (ndata.get("object_type") or {}).get("name", "")
    if obj_type_raw:
        type_lv = _TYPE_LV.get(obj_type_raw.lower().strip(), obj_type_raw)
        desc_parts.append(f"Veids: {type_lv}")

    shape_lv = _tlv(ndata.get("shape"), _SHAPE_LV)
    if shape_lv:
        desc_parts.append(f"Forma: {shape_lv}")

    edge = ndata.get("edge") or {}
    edge_desc = edge.get("description")
    if edge_desc:
        edge_lv = _tlv(edge_desc, _EDGE_LV)
        edge_label = edge.get("label") or edge_desc
        edge_label_lv = _tlv(edge_label, _EDGE_LV)
        desc_parts.append(f"Mala: {edge_label_lv or edge_lv}")

    orientation_raw = ndata.get("orientation") or ""
    if orientation_raw:
        orient_lv = _tlv(orientation_raw, _ORIENT_LV)
        desc_parts.append(f"Orientācija: {orient_lv}")

    rulers = ndata.get("ruler") or []
    if rulers:
        ruler_names = ", ".join(r.get("name", "") for r in rulers if r.get("name"))
        if ruler_names:
            desc_parts.append(f"Valdnieks: {ruler_names}")

    comments = ndata.get("comments", "")
    if comments:
        clean = re.sub(r"<[^>]+>", "", comments).strip()
        if clean:
            desc_parts.append(clean)

    description = "\n".join(desc_parts) or None

    # ── Kategorija ──────────────────────────────────────────────────
    obj_type = obj_type_raw.lower()
    if "commemorative" in obj_type:
        coin_cat = "commemorative"
    elif ("non-circulating" in obj_type or "collector" in obj_type
          or "bullion" in obj_type or "proof" in obj_type
          or "pattern" in obj_type):
        coin_cat = "collector"
    else:
        coin_cat = "circulation"

    item = CatalogItem(
        period_id=period.id,
        section=section,
        coin_category=coin_cat,
        name=ndata.get("title", "Nezināms"),
        year=year_str,
        denomination=denomination,
        material=material,
        weight_g=str(weight) if weight else None,
        diameter_mm=str(diameter) if diameter else None,
        catalog_number=catalog_number,
        mint=mint,
        mintage=mintage_str,
        designer=designer_str,
        engraver=engraver_str,
        description=description,
        obverse_description=obverse_description,
        reverse_description=reverse_description,
        image_url=local_obv,
        image_url_reverse=local_rev,
        numista_id=str(body.numista_id),
        admin_edited=True,
        is_approved=True,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "name": item.name, "numista_id": item.numista_id}
