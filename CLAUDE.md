# Kolekcija — Claude darba instrukcijas

## Backend palaišana
```powershell
C:\Users\USER\kolekcija\start-backend.ps1
```
Pēc JEBKURA backend koda labojuma — restartē ar šo skriptu. Uvicorn --reload NE VIENMĒR uztver izmaiņas.

---

## Arhitektūras noteikumi (NEDRĪKST pārkāpt)

### Katalogs un apstiprināšana
- `CatalogItem.is_approved=False` — priekšmets gaida admin apstiprinājumu, NAV redzams publiskajā katalogā
- `CatalogItem.is_approved=True` — apstiprināts, redzams katalogā
- `POST /catalog/from-recognition` vienmēr rada `is_approved=False` (bez `is_approved` lauka — default ir False)
- `GET /catalog/items` — filtrē `is_approved=True` (publiskais katalogs)
- `GET /admin/catalog` — filtrē `is_approved=True` (admin redz tikai apstiprinātos)
- Admin apstiprina caur `POST /admin/pending-catalog/{id}/approve` vai `POST /admin/pending/{id}/approve`

### Kolekcija
- `CollectionItem.catalog_item_id` — saite uz katalogu (var būt None)
- Ja `catalog_item_id=None` → priekšmets gaida admin manuālu apstiprināšanu (`GET /admin/pending`)
- Ja `catalog_item_id` norāda uz `is_approved=False` → gaida auto-apstiprināšanu (`GET /admin/pending-catalog`)
- `item_type`: "collection" | "trade" | "wishlist"

### Admin/lietotāja robeža
- Admin pārvalda KATALOGU — lietotāja kolekcijas dati ir neatkarīgi
- Kad admin DZĒŠ kataloga priekšmetu → OBLIGĀTI jākopē dati uz `custom_*` laukiem CollectionItem
- Kad admin NORAIDA pending-catalog → OBLIGĀTI jākopē dati uz `custom_*` laukiem

---

## Atkārtotās kļūdas — UZMANIES

### 1. Apraksta pazušana (admin_delete / admin_reject)
**Kļūda:** `ci.custom_description = ci.custom_description or item.description`
→ Ja `item.description=None` bet `obverse_description` ir aizpildīts, apraksts pazūd.

**Labojums:** Vienmēr izmanto `_full_description(item)` no `admin.py`:
```python
def _full_description(item: CatalogItem) -> str | None:
    parts = [
        item.description,
        f"Priekšpuse: {item.obverse_description}" if item.obverse_description else None,
        f"Aizmugure: {item.reverse_description}" if item.reverse_description else None,
    ]
    result = "\n\n".join(p for p in parts if p)
    return result or None
```

### 2. Priekšmets nonāk katalogā apejot admin
**Kļūda:** `GET /admin/catalog` bez `is_approved` filtra → rāda neapstiprinātos.
**Labojums:** `q = select(CatalogItem).where(CatalogItem.is_approved.is_(True))`

### 3. Recognition 500 kļūda
**Kļūda:** Backend nerestartēts, vai `e.message` neeksistē SDK versijā.
**Labojums:** Izmanto `str(e)` nevis `e.message`. Globālais handler `main.py`.
Vienmēr restartē backendu pēc izmaiņām.

### 4. is_approved=True aizmirsts pie admin approve
**Kļūda:** `admin_approve_pending` rada `CatalogItem` bez `is_approved=True`.
**Labojums:** `CatalogItem(..., is_approved=True)` — OBLIGĀTI.

---

## Failu karte

| Fails | Loma |
|-------|------|
| `backend/app/routes/catalog.py` | Publiskais katalogs + `from-recognition` |
| `backend/app/routes/admin.py` | Admin funkcijas (katalogs + iesniegumi) |
| `backend/app/routes/collection.py` | Lietotāja kolekcija |
| `backend/app/services/ai_service.py` | Anthropic API integrācija |
| `web/src/pages/Collection.jsx` | Kolekcijas UI (pārvaldība) |
| `web/src/pages/Catalog.jsx` | Kataloga UI (tikai lasīšana lietotājam) |
| `web/src/pages/Admin.jsx` | Admin panelis |
| `web/src/components/RecognizeModal.jsx` | AI atpazīšanas modālis |

---

## Stack
- Backend: FastAPI + SQLAlchemy async + SQLite (`kolekcija.db`)
- Frontend: React + Vite + React Query
- AI: Anthropic claude-opus-4-7 (caur `ai_service.py`)
- Ports: backend=8001, frontend=5173
