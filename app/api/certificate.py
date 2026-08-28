import io
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.auth import require_authenticated_user

router = APIRouter(prefix="/api/certificate", tags=["certificate"])
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
CERTIFICATE_ARTWORK = (
    Path(__file__).resolve().parents[2]
    / "frontend"
    / "src"
    / "assets"
    / "file_0000000069b8820eabdc9a847fdeaa19.png"
)


class CertificateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=180)
    completed_at: str
    typed_signature: bool = True
    logo_data_uri: str = ""


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-zÀ-ÿ0-9]+", "-", name.strip()).strip("-")
    return cleaned or "aluno"


def _parse_completed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Data de conclusão inválida.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SAO_PAULO)
    return parsed.astimezone(SAO_PAULO)


@router.post("/pdf")
def certificate_pdf(
    payload: CertificateRequest,
    session: dict = Depends(require_authenticated_user),
):
    if not session.get("sub"):
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    if not CERTIFICATE_ARTWORK.exists():
        raise HTTPException(status_code=500, detail="Arte oficial do certificado não encontrada.")

    completed_at = _parse_completed_at(payload.completed_at)
    name = payload.name.strip()

    buffer = io.BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(width, height), pageCompression=1)
    pdf.setTitle(f"Certificado de Conclusão - {name}")
    pdf.setAuthor("Clínica da Construção Civil")
    pdf.setSubject("Certificado de Conclusão - Curso de Elétrica e Hidráulica")

    # A arte validada é imutável: ocupa a página inteira sem reconstrução.
    artwork = ImageReader(str(CERTIFICATE_ARTWORK))
    pdf.drawImage(artwork, 0, 0, width=width, height=height, preserveAspectRatio=False, mask="auto")

    # Únicas sobreposições permitidas: assinatura/nome do aluno, data e horário.
    if payload.typed_signature:
        pdf.setFillColor(colors.HexColor("#151515"))
        pdf.setFont("Helvetica-Oblique", 20)
        pdf.drawCentredString(width / 2, 344, name)

    date_text = completed_at.strftime("%d/%m/%Y")
    time_text = completed_at.strftime("%H:%M")
    pdf.setFillColor(colors.HexColor("#151515"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(216, 76, date_text)
    pdf.drawString(222, 48, time_text)

    pdf.showPage()
    pdf.save()
    data = buffer.getvalue()
    filename = f"Certificado-{_safe_filename(name)}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
