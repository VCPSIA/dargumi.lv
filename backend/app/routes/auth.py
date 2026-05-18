from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models.user import User, UserSubscription
from app.models.catalog import AppSettings
from app.models.collection import CollectionItem
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut
from app.services import auth_service
import secrets, asyncio, smtplib, datetime, re
from email.mime.text import MIMEText
from app.config import settings
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()

async def current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = auth_service.decode_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/register", response_model=Token)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await auth_service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username taken")
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=auth_service.hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Token(access_token=auth_service.create_token(user.id))

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(db, data.email)
    if not user or not auth_service.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=auth_service.create_token(user.id))

@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return user


@router.get("/premium-status")
async def premium_status(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    settings_r = await db.execute(select(AppSettings).where(AppSettings.id == 1))
    s = settings_r.scalar_one_or_none()

    count_r = await db.execute(
        select(func.count()).select_from(CollectionItem).where(CollectionItem.user_id == user.id)
    )
    item_count = count_r.scalar()

    now = datetime.datetime.utcnow()
    sub_r = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.id, UserSubscription.is_active.is_(True))
        .where(or_(UserSubscription.end_date.is_(None), UserSubscription.end_date > now))
    )
    sub = sub_r.scalar_one_or_none()

    return {
        "premium_enabled": s.premium_enabled if s else False,
        "free_limit": s.premium_free_limit if s else 50,
        "price_monthly": s.premium_price_monthly if s else 2.99,
        "price_yearly": s.premium_price_yearly if s else 19.99,
        "item_count": item_count,
        "has_subscription": sub is not None,
        "subscription": {
            "plan": sub.plan,
            "end_date": sub.end_date.isoformat() if sub and sub.end_date else None,
        } if sub else None,
    }


def _send_email(to: str, subject: str, body: str):
    if not settings.smtp_user:
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as s:
        s.starttls()
        s.login(settings.smtp_user, settings.smtp_password)
        s.send_message(msg)


@router.post("/forgot-password")
async def forgot_password(payload: dict, db: AsyncSession = Depends(get_db)):
    email = (payload.get("email") or "").strip().lower()
    user = await auth_service.get_user_by_email(db, email)
    # Vienmēr atgriež 200 — neatklāj vai e-pasts eksistē
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        await db.commit()
        link = f"{settings.frontend_url}/reset-password?token={token}"
        body = f"Lai atjaunotu paroli, klikšķini uz saiti (derīga 1 stundu):\n\n{link}\n\nJa tu nepieprasīji paroles atjaunošanu, ignorē šo e-pastu."
        await asyncio.to_thread(_send_email, user.email, "Paroles atjaunošana — Dārgumi.lv", body)
    return {"ok": True}


@router.post("/reset-password")
async def reset_password(payload: dict, db: AsyncSession = Depends(get_db)):
    token = (payload.get("token") or "").strip()
    new_password = payload.get("password") or ""
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Parole pārāk īsa (min. 6 simboli)")
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if not user or not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Saite nav derīga")
    if datetime.datetime.utcnow() > user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Saite ir beigusies (derīga 1 stundu)")
    user.hashed_password = auth_service.hash_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    await db.commit()
    return {"ok": True}


async def _upsert_oauth_user(
    db: AsyncSession,
    email: str,
    name: str,
    provider: str,
    provider_id: str,
) -> User:
    """Atrod vai izveido lietotāju pēc OAuth datu."""
    id_field = f"{provider}_id"

    # 1. Meklē pēc provider ID
    result = await db.execute(select(User).where(getattr(User, id_field) == provider_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    # 2. Meklē pēc e-pasta — pievieno OAuth ID esošam kontam
    if email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            setattr(user, id_field, provider_id)
            await db.commit()
            return user

    # 3. Izveido jaunu lietotāju
    base = re.sub(r"[^a-z0-9]", "", (name or email.split("@")[0]).lower()) or "user"
    username = base
    suffix = 1
    while True:
        r = await db.execute(select(User).where(User.username == username))
        if not r.scalar_one_or_none():
            break
        username = f"{base}{suffix}"
        suffix += 1

    user = User(
        email=email or f"{provider}_{provider_id}@oauth.local",
        username=username,
        hashed_password="",
        **{id_field: provider_id},
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/google")
async def google_login(payload: dict, db: AsyncSession = Depends(get_db)):
    token = payload.get("token") or ""
    if not token:
        raise HTTPException(status_code=400, detail="Nav token")
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": token},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Google token nav derīgs")
    data = r.json()
    if settings.google_client_id and data.get("aud") != settings.google_client_id:
        raise HTTPException(status_code=401, detail="Google client_id neatbilst")
    user = await _upsert_oauth_user(
        db,
        email=data.get("email", ""),
        name=data.get("name", ""),
        provider="google",
        provider_id=data["sub"],
    )
    return Token(access_token=auth_service.create_token(user.id))


@router.post("/facebook")
async def facebook_login(payload: dict, db: AsyncSession = Depends(get_db)):
    token = payload.get("token") or ""
    if not token:
        raise HTTPException(status_code=400, detail="Nav token")

    # Verificē ar App Secret ja iestatīts, citādi izmanto ME endpoint tieši
    if settings.facebook_app_id and settings.facebook_app_secret:
        app_token = f"{settings.facebook_app_id}|{settings.facebook_app_secret}"
        async with httpx.AsyncClient() as client:
            vr = await client.get(
                "https://graph.facebook.com/debug_token",
                params={"input_token": token, "access_token": app_token},
            )
        if vr.status_code != 200 or not vr.json().get("data", {}).get("is_valid"):
            raise HTTPException(status_code=401, detail="Facebook token nav derīgs")

    async with httpx.AsyncClient() as client:
        me = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,name,email", "access_token": token},
        )
    if me.status_code != 200 or "id" not in me.json():
        raise HTTPException(status_code=401, detail="Facebook dati nav pieejami")
    data = me.json()
    user = await _upsert_oauth_user(
        db,
        email=data.get("email", ""),
        name=data.get("name", ""),
        provider="facebook",
        provider_id=data["id"],
    )
    return Token(access_token=auth_service.create_token(user.id))
