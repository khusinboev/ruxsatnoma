"""Add permits table

Revision ID: 002
Revises: 001
Create Date: 2026-07-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "permits",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False),
        sa.Column("permit_id", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("passport_number", sa.String(length=50), nullable=False),
        sa.Column("jshshir", sa.String(length=20), nullable=False),
        sa.Column("birth_date", sa.String(length=20), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("file_id", sa.String(length=255), nullable=True),
        sa.Column("file_unique_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "permit_id", name="uq_permits_user_permit"),
    )
    op.create_index("idx_permits_user_id", "permits", ["user_id"])
    op.create_index("idx_permits_permit_id", "permits", ["permit_id"])
    op.create_index("idx_permits_created_at", "permits", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_permits_created_at", table_name="permits")
    op.drop_index("idx_permits_permit_id", table_name="permits")
    op.drop_index("idx_permits_user_id", table_name="permits")
    op.drop_table("permits")
