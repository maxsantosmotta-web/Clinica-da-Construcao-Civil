from urllib.request import Request as UrlRequest, urlopen

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/videos", tags=["videos"])

LESSON_VIDEO_URLS = {
    1: "https://drive.google.com/uc?export=download&id=1UCl-EffvwcnUtoqCcGgqJz1k6s-FwZk7",
}


def _iter_upstream(response, chunk_size: int = 1024 * 512):
    try:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            yield chunk
    finally:
        response.close()


@router.get("/aula-{lesson_id}")
def stream_lesson_video(lesson_id: int, request: Request):
    source_url = LESSON_VIDEO_URLS.get(lesson_id)
    if not source_url:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "video/mp4,video/*;q=0.9,*/*;q=0.8",
    }
    range_header = request.headers.get("range")
    if range_header:
        headers["Range"] = range_header

    upstream_request = UrlRequest(source_url, headers=headers)
    try:
        upstream = urlopen(upstream_request, timeout=30)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Não foi possível carregar o vídeo.") from exc

    response_headers = {
        "Accept-Ranges": upstream.headers.get("Accept-Ranges", "bytes"),
        "Cache-Control": "private, max-age=3600",
    }
    for header_name in ("Content-Length", "Content-Range"):
        value = upstream.headers.get(header_name)
        if value:
            response_headers[header_name] = value

    status_code = getattr(upstream, "status", 200)
    content_type = upstream.headers.get("Content-Type", "video/mp4")
    if "text/html" in content_type.lower():
        upstream.close()
        raise HTTPException(status_code=502, detail="A origem não entregou o arquivo de vídeo.")

    return StreamingResponse(
        _iter_upstream(upstream),
        status_code=status_code,
        media_type=content_type,
        headers=response_headers,
    )
