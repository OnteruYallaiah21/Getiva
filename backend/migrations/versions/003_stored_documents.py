"""stored_documents for admin Supabase uploads (URL in Neon)

Revision ID: 003
Revises: 002
Create Date: 2026-04-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "stored_documents" in inspector.get_table_names():
        return
    op.create_table(
        "stored_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(512), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stored_documents_uploaded_by_id"),
        "stored_documents",
        ["uploaded_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stored_documents_uploaded_by_id"), table_name="stored_documents")
    op.drop_table("stored_documents")
