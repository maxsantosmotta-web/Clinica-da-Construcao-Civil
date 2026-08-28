"""Persist issued course certificates and cap issuance at two versions.

Revision ID: 20260828_0007
Revises: 20260716_0006
Create Date: 2026-08-28
"""

from alembic import op
import sqlalchemy as sa

revision = "20260828_0007"
down_revision = "20260716_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "certificate_issues",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("issue_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("typed_signature", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("pdf_content", sa.LargeBinary(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("user_id"),
        sa.CheckConstraint("issue_count >= 1 AND issue_count <= 2", name="ck_certificate_issues_issue_count"),
    )


def downgrade() -> None:
    op.drop_table("certificate_issues")
