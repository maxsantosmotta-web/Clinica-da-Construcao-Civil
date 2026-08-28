import base64
import io
import re
from datetime import datetime
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


def _logo_reader(data_uri: str):
    if not data_uri or "," not in data_uri:
        return None
    try:
        encoded = data_uri.split(",", 1)[1]
        return ImageReader(io.BytesIO(base64.b64decode(encoded)))
    except Exception:
        return None


@router.post("/pdf")
def certificate_pdf(
    payload: CertificateRequest,
    session: dict = Depends(require_authenticated_user),
):
    if not session.get("sub"):
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    completed_at = _parse_completed_at(payload.completed_at)
    name = payload.name.strip()

    buffer = io.BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(width, height), pageCompression=1)
    pdf.setTitle(f"Certificado de Conclusão - {name}")
    pdf.setAuthor("Clínica da Construção Civil")
    pdf.setSubject("Certificado de Conclusão - Curso de Elétrica e Hidráulica")

    gold = colors.HexColor("#B38B2E")
    navy = colors.HexColor("#1D2D3B")
    cream = colors.HexColor("#FFFDF8")
    pale = colors.HexColor("#FFFAF0")
    grey = colors.HexColor("#46535B")

    pdf.setFillColor(cream)
    pdf.rect(0, 0, width, height, stroke=0, fill=1)

    margin = 34
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(2.4)
    pdf.rect(margin, margin, width - (2 * margin), height - (2 * margin), stroke=1, fill=0)
    pdf.setStrokeColor(navy)
    pdf.setLineWidth(0.7)
    pdf.rect(margin + 7, margin + 7, width - (2 * (margin + 7)), height - (2 * (margin + 7)), stroke=1, fill=0)

    logo = _logo_reader(payload.logo_data_uri)
    if logo:
        try:
            pdf.drawImage(logo, 54, height - 123, width=72, height=72, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(138, height - 82, "CLÍNICA DA CONSTRUÇÃO CIVIL")

    pdf.setFillColor(gold)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(width / 2, height - 92, "CERTIFICADO")
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 112, "DE CONCLUSÃO")

    pdf.setFont("Helvetica", 8.5)
    pdf.drawCentredString(width / 2, height - 151, "CERTIFICAMOS PARA OS DEVIDOS FINS QUE")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 184, name)
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(0.7)
    pdf.line(190, height - 191, width - 190, height - 191)

    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(navy)
    pdf.drawCentredString(width / 2, height - 220, "Concluiu com êxito o treinamento completo com a carga horária de 40h,")
    pdf.drawCentredString(width / 2, height - 238, "do curso de elétrica e hidráulica.")

    box_x, box_y, box_w, box_h = 148, 185, width - 296, 118
    pdf.setFillColor(pale)
    pdf.setStrokeColor(colors.HexColor("#D7C48D"))
    pdf.roundRect(box_x, box_y, box_w, box_h, 7, stroke=1, fill=1)

    pdf.setFillColor(gold)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(width / 2, box_y + box_h - 19, "ESPECIFICAÇÕES DO CONTEÚDO QUE COMPÔS O CURSO")

    left_x = box_x + 42
    right_x = width / 2 + 38
    top = box_y + box_h - 42

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left_x, top, "ELÉTRICA")
    pdf.drawString(right_x, top, "HIDRÁULICA")
    pdf.setFont("Helvetica", 7.8)

    electric = [
        "Instalação de tomadas",
        "Chuveiros elétricos",
        "Interruptores e lâmpadas",
        "Quadros de Distribuição",
        "Normas NR10",
    ]
    hydraulic = [
        "Instalações residenciais",
        "Pressurização de rede",
        "Redes de água e esgoto",
        "Reparos e Vazamentos",
        "Reservatórios",
    ]
    for idx, item in enumerate(electric):
        pdf.drawString(left_x, top - 17 - (idx * 13), item)
    for idx, item in enumerate(hydraulic):
        pdf.drawString(right_x, top - 17 - (idx * 13), item)

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica-Bold", 7.3)
    pdf.drawCentredString(width / 2, 157, "CURSO DE FORMAÇÃO LIVRE, NÃO PROFISSIONALIZANTE.")
    pdf.drawCentredString(width / 2, 146, "NÃO CONFERE HABILITAÇÃO PROFISSIONAL.")

    date_text = completed_at.strftime("%d/%m/%Y")
    time_text = completed_at.strftime("%H:%M")
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(73, 103, "CONCLUSÃO")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(73, 89, f"Data: {date_text}")
    pdf.drawString(73, 77, f"Hora: {time_text}")

    student_x = width / 2 - 142
    student_w = 120
    responsible_x = width / 2 + 44
    responsible_w = 145
    sign_y = 82

    pdf.setStrokeColor(navy)
    pdf.line(student_x, sign_y, student_x + student_w, sign_y)
    pdf.line(responsible_x, sign_y, responsible_x + responsible_w, sign_y)

    if payload.typed_signature:
        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.drawCentredString(student_x + (student_w / 2), sign_y + 8, name)

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 6.8)
    pdf.drawCentredString(student_x + (student_w / 2), sign_y - 12, "ASSINATURA DO ALUNO")

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(responsible_x + (responsible_w / 2), sign_y + 8, "Clínica da Construção Civil")
    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 6.8)
    pdf.drawCentredString(responsible_x + (responsible_w / 2), sign_y - 12, "RESPONSÁVEL PELO CURSO")

    seal_x = width / 2
    seal_y = 80
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(1.4)
    pdf.circle(seal_x, seal_y, 25, stroke=1, fill=0)
    pdf.setFillColor(gold)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(seal_x, seal_y + 2, "CCC")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawCentredString(seal_x, seal_y - 9, "40H")

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
