import io
import re
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import Boolean, DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.auth import require_authenticated_user
from app.database import Base, session_scope

router = APIRouter(prefix="/api/certificate", tags=["certificate"])
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
CERTIFICATE_ARTWORK = Path(__file__).resolve().parent.parent / "assets" / "certificate-template.png"
# Certificados já emitidos antes desta correção visual são regravados uma única vez,
# sem consumir nova emissão, para receber apenas o alinhamento corrigido de data/horário.
CERTIFICATE_LAYOUT_UPDATED_AT = datetime(2026, 8, 28, 22, 45, tzinfo=timezone.utc)


class CertificateIssue(Base):
    __tablename__ = "certificate_issues"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    issue_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    typed_signature: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    pdf_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CertificateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=180)
    completed_at: str
    typed_signature: bool = True


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


def _render_certificate(name: str, completed_at: datetime, typed_signature: bool) -> bytes:
    if not CERTIFICATE_ARTWORK.exists():
        raise HTTPException(status_code=500, detail="Arte oficial do certificado não encontrada.")

    buffer = io.BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(width, height), pageCompression=1)
    pdf.setTitle(f"Certificado de Conclusão - {name}")
    pdf.setAuthor("Clínica da Construção Civil")
    pdf.setSubject("Certificado de Conclusão - Curso de Elétrica e Hidráulica")

    artwork = ImageReader(str(CERTIFICATE_ARTWORK))
    pdf.drawImage(artwork, 0, 0, width=width, height=height, preserveAspectRatio=False, mask="auto")

    if typed_signature:
        pdf.setFillColor(colors.HexColor("#151515"))
        pdf.setFont("Helvetica-Oblique", 20)
        pdf.drawCentredString(width / 2, 344, name)

    local_completed_at = completed_at.astimezone(SAO_PAULO) if completed_at.tzinfo else completed_at.replace(tzinfo=SAO_PAULO)
    date_text = local_completed_at.strftime("%d/%m/%Y")
    time_text = local_completed_at.strftime("%H:%M")
    pdf.setFillColor(colors.HexColor("#151515"))
    pdf.setFont("Helvetica-Bold", 8.5)
    # A arte oficial já contém as duas linhas. Centraliza somente os valores sobre cada campo.
    pdf.drawCentredString(318, 74, date_text)
    pdf.drawCentredString(292, 46, time_text)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _pdf_response(issue: CertificateIssue, *, inline: bool = True) -> Response:
    disposition = "inline" if inline else "attachment"
    return Response(
        content=issue.pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'{disposition}; filename="{issue.filename}"',
            "Cache-Control": "no-store, max-age=0",
        },
    )


def _refresh_saved_layout_once(issue: CertificateIssue, db) -> None:
    updated_at = issue.updated_at
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    if updated_at >= CERTIFICATE_LAYOUT_UPDATED_AT:
        return

    issue.pdf_content = _render_certificate(issue.name, issue.completed_at, issue.typed_signature)
    issue.updated_at = datetime.now(timezone.utc)
    db.flush()


@router.get("/status")
def certificate_status(session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    with session_scope() as db:
        issue = db.get(CertificateIssue, user_id)
        if not issue:
            return {"issued": False, "issue_count": 0, "remaining_corrections": 1, "locked": False}
        return {
            "issued": True,
            "issue_count": issue.issue_count,
            "remaining_corrections": max(0, 2 - issue.issue_count),
            "locked": issue.issue_count >= 2,
            "name": issue.name,
            "typed_signature": issue.typed_signature,
            "completed_at": issue.completed_at.isoformat(),
            "filename": issue.filename,
        }


@router.post("/issue")
def issue_certificate(payload: CertificateRequest, session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    completed_at = _parse_completed_at(payload.completed_at)
    name = payload.name.strip()

    with session_scope() as db:
        issue = db.query(CertificateIssue).filter(CertificateIssue.user_id == user_id).with_for_update().one_or_none()
        current_count = issue.issue_count if issue else 0
        if current_count >= 2:
            raise HTTPException(status_code=409, detail="O limite de duas emissões deste certificado já foi utilizado.")

        pdf_content = _render_certificate(name, completed_at, payload.typed_signature)
        new_count = current_count + 1
        filename = f"Certificado-{_safe_filename(name)}.pdf"

        if issue is None:
            issue = CertificateIssue(
                user_id=user_id,
                issue_count=new_count,
                name=name,
                typed_signature=payload.typed_signature,
                completed_at=completed_at,
                filename=filename,
                pdf_content=pdf_content,
            )
            db.add(issue)
        else:
            issue.issue_count = new_count
            issue.name = name
            issue.typed_signature = payload.typed_signature
            issue.completed_at = completed_at
            issue.filename = filename
            issue.pdf_content = pdf_content
            issue.updated_at = datetime.now(timezone.utc)

        db.flush()
        return _pdf_response(issue)


@router.get("/pdf")
def current_certificate_pdf(session: dict = Depends(require_authenticated_user)):
    user_id = session.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    with session_scope() as db:
        issue = db.get(CertificateIssue, user_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Certificado ainda não emitido.")
        _refresh_saved_layout_once(issue, db)
        return _pdf_response(issue)
