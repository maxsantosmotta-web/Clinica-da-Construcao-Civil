from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from app.auth import require_authenticated_user
from app.database import session_scope
from app.models import UserAvatar, UserProfile

router = APIRouter(prefix="/api/profile", tags=["profile"])

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_BYTES = 5 * 1024 * 1024


class ProfilePayload(BaseModel):
    full_name: str = Field(min_length=3, max_length=180)
    phone: str = Field(min_length=8, max_length=30)
    birth_date: str = Field(min_length=10, max_length=10)


def _digits(value: str) -> str:
    return "".join(char for char in (value or "") if char.isdigit())


def _parse_birth_date(value: str) -> date:
    try:
        return datetime.strptime((value or "").strip(), "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Informe a data de nascimento no formato DD/MM/AAAA.")


def _age_on_today(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _serialize(profile: UserProfile | None, has_avatar: bool = False) -> dict:
    if profile is None:
        return {"completed": False, "hasAvatar": has_avatar, "profile": None}
    return {
        "completed": bool(profile.completed),
        "hasAvatar": has_avatar,
        "profile": {
            "fullName": profile.full_name,
            "phone": profile.phone,
            "birthDate": profile.birth_date.strftime("%d/%m/%Y") if profile.birth_date else "",
        },
    }


@router.get("")
def get_profile(session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    with session_scope() as db:
        return _serialize(db.get(UserProfile, user_id), db.get(UserAvatar, user_id) is not None)


@router.put("")
def save_profile(payload: ProfilePayload, session: dict = Depends(require_authenticated_user)):
    phone = _digits(payload.phone)
    birth_date = _parse_birth_date(payload.birth_date)

    if len(phone) < 10:
        raise HTTPException(status_code=400, detail="Informe um telefone válido com DDD.")
    if birth_date >= date.today():
        raise HTTPException(status_code=400, detail="Informe uma data de nascimento válida.")
    if _age_on_today(birth_date) < 18:
        raise HTTPException(status_code=400, detail="A Clínica da Construção Civil é destinada somente a maiores de 18 anos.")

    user_id = session.get("sub")
    with session_scope() as db:
        profile = db.get(UserProfile, user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            db.add(profile)

        profile.full_name = payload.full_name.strip()
        profile.phone = phone
        profile.birth_date = birth_date
        profile.completed = 1
        db.flush()
        return _serialize(profile, db.get(UserAvatar, user_id) is not None)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    session: dict = Depends(require_authenticated_user),
):
    mime_type = (file.content_type or "").lower()
    if mime_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="Envie uma foto JPG, PNG ou WEBP.")

    content = await file.read(MAX_AVATAR_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="A foto enviada está vazia.")
    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=413, detail="A foto deve ter no máximo 5 MB.")

    user_id = session.get("sub")
    with session_scope() as db:
        avatar = db.get(UserAvatar, user_id)
        if avatar is None:
            avatar = UserAvatar(user_id=user_id, mime_type=mime_type, size_bytes=len(content), content=content)
            db.add(avatar)
        else:
            avatar.mime_type = mime_type
            avatar.size_bytes = len(content)
            avatar.content = content
        db.flush()
        return {"saved": True, "mimeType": avatar.mime_type, "sizeBytes": avatar.size_bytes}


@router.get("/avatar")
def get_avatar(session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    with session_scope() as db:
        avatar = db.get(UserAvatar, user_id)
        if avatar is None:
            raise HTTPException(status_code=404, detail="Foto de perfil não cadastrada.")
        return Response(
            content=avatar.content,
            media_type=avatar.mime_type,
            headers={"Cache-Control": "private, max-age=300"},
        )


@router.delete("/avatar", status_code=204)
def delete_avatar(session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    with session_scope() as db:
        avatar = db.get(UserAvatar, user_id)
        if avatar is not None:
            db.delete(avatar)
    return Response(status_code=204)
