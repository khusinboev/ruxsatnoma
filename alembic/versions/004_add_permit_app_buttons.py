"""Add permit_app_buttons table

Revision ID: 004
Revises: 003
Create Date: 2026-07-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "permit_app_buttons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("button_text", sa.String(length=255), nullable=False),
        sa.Column("button_url", sa.String(length=512), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("added_by", sa.BigInteger(), sa.ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("button_text", "button_url", name="uq_permit_app_buttons_text_url"),
    )


def downgrade() -> None:
    op.drop_table("permit_app_buttons")
