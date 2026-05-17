import base64
import io
import json
import httpx
import anthropic
from PIL import Image
from app.config import settings
from app.schemas.recognition import RecognitionResult

MAX_BYTES = 3 * 1024 * 1024  # 3MB raw → ~4MB base64, droši zem Claude 5MB limita

def _compress(image_bytes: bytes, content_type: str) -> tuple[bytes, str]:
    """Samazina attēlu ja tas pārsniedz MAX_BYTES."""
    if len(image_bytes) <= MAX_BYTES:
        return image_bytes, content_type
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P", "CMYK"):
            img = img.convert("RGB")
        quality = 85
        while True:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= MAX_BYTES:
                return data, "image/jpeg"
            w, h = img.size
            img = img.resize((int(w * 0.8), int(h * 0.8)), Image.LANCZOS)
            quality = max(quality - 10, 20)
    except Exception:
        # Ja Pillow nevar apstrādāt, atgriež oriģinālu (Claude pats ziņos par kļūdu)
        return image_bytes, content_type

client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    http_client=httpx.Client(verify=False),
)

SYSTEM_PROMPT = """You are an expert numismatist and philatelist. You identify coins, medals, stamps and banknotes from photos.
Respond ONLY with a valid JSON object. No markdown, no explanation — just JSON.

LANGUAGE RULES (strictly follow):
- "name": write in LATVIAN (e.g. "Latvijas 1 Lats 1924. gads")
- "description": write in LATVIAN
- "obverse_description": write in LATVIAN
- "reverse_description": write in LATVIAN
- "notes": write in LATVIAN
- "country": write in ENGLISH (required for database lookup, e.g. "Latvia", "France", "Germany")
- All other fields: use standard international formats (numbers, codes, etc.)

JSON structure:
{
  "recognized": true/false,
  "section": "coins" | "medals" | "stamps" | "banknotes",
  "name": "pilns nosaukums latviski",
  "year": "gads vai diapazons, piem. 2018",
  "country": "country name in English",
  "denomination": "nominālvērtība un valūta, piem. 1 Eiro",
  "material": "metāls vai materiāls, piem. Bimetālisks",
  "diameter_mm": "diametrs mm kā skaitlis",
  "weight_g": "svars gramos kā skaitlis",
  "mint": "kaltuves nosaukums",
  "mintage": "izlaisto eksemplāru skaits",
  "obverse_description": "sīks priekšpuses apraksts latviski",
  "reverse_description": "sīks aizmugures apraksts latviski",
  "perforation": "perforācijas mērījums (tikai pastmarkām)",
  "color": "krāsu apraksts (tikai pastmarkām)",
  "catalog_number": "kataloga atsauce, piem. KM#123 vai Scott#45",
  "description": "īss vispārīgs apraksts latviski",
  "coin_category": "circulation" | "commemorative" | "collector",
  "confidence": 0.0-1.0,
  "notes": "papildu info vai nenoteiktība latviski"
}

coin_category rules:
- "circulation": regular coins used as everyday currency
- "commemorative": special issue coins commemorating events, persons, anniversaries
- "collector": proof coins, sets, bullion, limited editions not for circulation

If you cannot identify the item, set "recognized": false and fill only what you can determine.
"""

def _image_block(image_bytes: bytes, content_type: str) -> dict:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": content_type,
            "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
        },
    }

def _fix_ct(ct: str) -> str:
    return "image/jpeg" if ct == "image/jpg" else ct

async def recognize_image(
    obverse_bytes: bytes,
    obverse_ct: str,
    section_hint: str | None = None,
    reverse_bytes: bytes | None = None,
    reverse_ct: str | None = None,
) -> RecognitionResult:

    obverse_bytes, obverse_ct = _compress(obverse_bytes, _fix_ct(obverse_ct))
    if reverse_bytes:
        reverse_bytes, reverse_ct = _compress(reverse_bytes, _fix_ct(reverse_ct))

    content = []

    if reverse_bytes:
        content.append({"type": "text", "text": "Obverse (front):"})
        content.append(_image_block(obverse_bytes, obverse_ct))
        content.append({"type": "text", "text": "Reverse (back):"})
        content.append(_image_block(reverse_bytes, reverse_ct))
        text = f"Identify this {section_hint or 'collectible'} using both obverse and reverse images."
    else:
        content.append(_image_block(obverse_bytes, obverse_ct))
        text = f"Identify this {section_hint or 'collectible'} collectible item."

    content.append({"type": "text", "text": text})

    import asyncio
    try:
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-opus-4-7",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
    except anthropic.BadRequestError as e:
        return RecognitionResult(recognized=False, notes=f"Attēls nav derīgs: {str(e)}")
    except anthropic.APIConnectionError as e:
        return RecognitionResult(recognized=False, notes=f"Nevar savienoties ar AI servisu: {str(e)}")
    except anthropic.APIError as e:
        return RecognitionResult(recognized=False, notes=f"AI kļūda: {str(e)}")
    except Exception as e:
        import traceback
        print(f"[AI ERROR] {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return RecognitionResult(recognized=False, notes=f"Kļūda: {type(e).__name__}: {e}")

    raw = response.content[0].text.strip()
    import sys
    sys.stdout.buffer.write(("[AI RAW RESPONSE]: " + raw[:500] + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()

    import re

    def _try_parse(text: str) -> RecognitionResult | None:
        try:
            data = json.loads(text)
            # Noņem laukus, kurus RecognitionResult nepazīst
            allowed = RecognitionResult.model_fields.keys()
            filtered = {k: v for k, v in data.items() if k in allowed}
            return RecognitionResult(**filtered)
        except Exception as e:
            print(f"[PARSE ERROR]: {e}")
            return None

    # 1. Tieši parsē
    result = _try_parse(raw)
    if result:
        return result

    # 2. Noņem markdown bloku
    block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if block:
        result = _try_parse(block.group(1))
        if result:
            return result

    # 3. Atrod { ... } robežas
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        result = _try_parse(raw[start:end])
        if result:
            return result

    preview = raw[:300].replace("\n", " ")
    return RecognitionResult(recognized=False, notes=f"Parsēšana neizdevās. AI atbildēja: {preview}")
