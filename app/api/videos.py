from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import select

from app.api.admin import CLINIC_OWNER_USER_ID
from app.database import session_scope
from app.models import LibraryAsset

router = APIRouter(prefix="/api/videos", tags=["videos"])

COURSE_VIDEO_NAMES = {
    1: "aula-1.mp4",
}


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


@router.get("/aula-{lesson_id}")
def stream_lesson_video(lesson_id: int, request: Request):
    expected_name = COURSE_VIDEO_NAMES.get(lesson_id)
    if not expected_name:
        raise HTTPException(status_code=404, detail="Vídeo não configurado para esta aula.")

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
                detail=f'Envie o arquivo "{expected_name}" para a Biblioteca do administrador.',
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
