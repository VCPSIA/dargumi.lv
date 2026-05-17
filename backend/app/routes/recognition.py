from fastapi import APIRouter, UploadFile, File, Query, Depends, HTTPException
from typing import Optional

from app.schemas.recognition import RecognitionResult
from app.services.ai_service import recognize_image
from app.models.catalog import SectionType
from app.routes.auth import current_user
from app.models.user import User

router = APIRouter(prefix="/recognize", tags=["recognition"])

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

def _validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP images allowed")

@router.post("", response_model=RecognitionResult)
async def recognize(
    obverse: UploadFile = File(..., description="Priekšpuse (averse)"),
    reverse: Optional[UploadFile] = File(None, description="Aizmugure (reverse) — tikai monētām/medaļām"),
    section: SectionType | None = Query(None),
    user: User = Depends(current_user),
):
    _validate(obverse)
    obverse_bytes = await obverse.read()
    if len(obverse_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Attēls pārāk liels (max 10MB)")

    reverse_bytes = None
    reverse_ct = None
    if reverse and reverse.filename:
        _validate(reverse)
        reverse_bytes = await reverse.read()
        if len(reverse_bytes) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="Attēls pārāk liels (max 10MB)")
        reverse_ct = reverse.content_type

    try:
        result = await recognize_image(
            obverse_bytes=obverse_bytes,
            obverse_ct=obverse.content_type,
            section_hint=section,
            reverse_bytes=reverse_bytes,
            reverse_ct=reverse_ct,
        )
    except Exception as e:
        from app.schemas.recognition import RecognitionResult
        result = RecognitionResult(recognized=False, notes=f"Servera kļūda: {type(e).__name__}: {e}")
    return result
