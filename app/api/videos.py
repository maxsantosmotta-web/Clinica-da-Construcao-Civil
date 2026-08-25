from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import select

from app.api.admin import CLINIC_OWNER_USER_ID
from app.auth import require_authenticated_user
from app.database import session_scope
from app.models import LibraryAsset

router = APIRouter(prefix="/api/videos", tags=["videos"])

MAX_COURSE_VIDEO_SIZE = 250 * 1024 * 1024


def _lesson_video_name(lesson_id: int) -> str:
    if lesson_id < 1 or lesson_id > 39:
        raise HTTPException(status_code=404, detail="Aula inválida.")
    return f"aula-{lesson_id}.mp4"


def _parse_range(range_header: str | None, total_size: int) -> tuple[int, int] | None:
    if not range_header or not range_header.startswith("bytes="):
        return None

    raw = range_header.removeprefix("bytes=").split(",", 1)[0].strip()
    if "-" not in raw:
        return None

    start_raw, end_raw = raw.split("-", 1)
    try:
        if start_raw:
            start = int(start_raw)
            end = int(end_raw) if end_raw else total_size - 1
        else:
            suffix_length = int(end_raw)
            if suffix_length <= 0:
                return None
            start = max(total_size - suffix_length, 0)
            end = total_size - 1
    except ValueError:
        return None

    if start < 0 or start >= total_size:
        return None

    end = min(end, total_size - 1)
    if end < start:
        return None

    return start, end


@router.post("/admin/aula-{lesson_id}", status_code=status.HTTP_201_CREATED)
async def upload_lesson_video(
    lesson_id: int,
    file: UploadFile = File(...),
    session: dict = Depends(require_authenticated_user),
):
    user_id = str(session.get("sub") or "").strip()
    if user_id != CLINIC_OWNER_USER_ID:
        raise HTTPException(status_code=403, detail="Apenas o administrador pode alterar as videoaulas.")

    expected_name = _lesson_video_name(lesson_id)
    content_type = (file.content_type or "").lower()
    if content_type and not content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Selecione um arquivo de vídeo válido.")

    content = await file.read(MAX_COURSE_VIDEO_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="O arquivo de vídeo está vazio.")
    if len(content) > MAX_COURSE_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="O vídeo ultrapassa o limite de 250 MB.",
        )

    with session_scope() as db:
        asset = db.scalar(
            select(LibraryAsset)
            .where(
                LibraryAsset.user_id == CLINIC_OWNER_USER_ID,
                LibraryAsset.name == expected_name,
            )
            .order_by(LibraryAsset.created_at.desc())
            .limit(1)
        )

        if asset is None:
            asset = LibraryAsset(
                user_id=CLINIC_OWNER_USER_ID,
                name=expected_name,
                mime_type=file.content_type or "video/mp4",
                size_bytes=len(content),
                content=content,
            )
            db.add(asset)
        else:
            asset.mime_type = file.content_type or "video/mp4"
            asset.size_bytes = len(content)
            asset.content = content

        db.flush()

    return {
        "status": "ok",
        "lessonId": lesson_id,
        "name": expected_name,
        "sizeBytes": len(content),
    }


@router.get("/aula-{lesson_id}")
def stream_lesson_video(lesson_id: int, request: Request):
    expected_name = _lesson_video_name(lesson_id)

    with session_scope() as db:
        asset = db.scalar(
            select(LibraryAsset)
            .where(
                LibraryAsset.user_id == CLINIC_OWNER_USER_ID,
                LibraryAsset.name == expected_name,
            )
            .order_by(LibraryAsset.created_at.desc())
            .limit(1)
        )

        if asset is None:
            raise HTTPException(
                status_code=404,
                detail=f'Vídeo "{expected_name}" ainda não foi enviado pelo administrador.',
            )

        content = bytes(asset.content)
        media_type = asset.mime_type or "video/mp4"

    total_size = len(content)
    selected_range = _parse_range(request.headers.get("range"), total_size)

    common_headers = {
        "Accept-Ranges": "bytes",
        "Cache-Control": "private, max-age=3600",
        "Content-Disposition": f'inline; filename="{expected_name}"',
    }

    if selected_range is None:
        common_headers["Content-Length"] = str(total_size)
        return Response(content=content, media_type=media_type, headers=common_headers)

    start, end = selected_range
    chunk = content[start : end + 1]
    common_headers.update(
        {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {start}-{end}/{total_size}",
        }
    )
    return Response(
        content=chunk,
        status_code=206,
        media_type=media_type,
        headers=common_headers,
    )
