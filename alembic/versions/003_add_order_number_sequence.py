"""Add persistent order_number sequence to permits

Revision ID: 003
Revises: 002
Create Date: 2026-07-02 12:00:00.000000

The previous approach computed "buyurtma tartib raqami" on the fly as
`permit.id + settings.ORDER_NUMBER_OFFSET`. That's not truly persisted:
if ORDER_NUMBER_OFFSET in .env is ever changed, the displayed number for
every record (old and new) would shift.

This migration:
  1) Adds a real `order_number` column to `permits`.
  2) Backfills existing rows using the SAME formula that was used until
     now (id + ORDER_NUMBER_OFFSET), so numbers users already received
     stay valid and unchanged.
  3) Creates a PostgreSQL SEQUENCE that continues exactly where the
     backfilled values left off, and attaches it as the column's
     server-side default.

After this migration, ORDER_NUMBER_OFFSET in .env is only relevant the
very first time this migration ever runs (it seeds the starting point).
From then on, the database (the sequence) is the single source of truth
for order numbers, completely independent of .env.
"""
from alembic import op
import sqlalchemy as sa

from bot.config.settings import settings


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

SEQUENCE_NAME = "permits_order_number_seq"


def upgrade() -> None:
    conn = op.get_bind()

    # 1) Add the column as nullable first so we can backfill it.
    op.add_column("permits", sa.Column("order_number", sa.BigInteger(), nullable=True))

    # 2) Backfill existing rows with the old formula (id + OFFSET), so
    #    numbers already shown to users remain unchanged.
    conn.execute(
        sa.text("UPDATE permits SET order_number = id + :offset"),
        {"offset": settings.ORDER_NUMBER_OFFSET},
    )

    # 3) Now that every row has a value, enforce NOT NULL + UNIQUE.
    op.alter_column("permits", "order_number", nullable=False)
    op.create_unique_constraint("uq_permits_order_number", "permits", ["order_number"])
    op.create_index("idx_permits_order_number", "permits", ["order_number"])

    # 4) Create a sequence that continues right after the highest value
    #    currently in use (falls back to OFFSET if the table is empty).
    max_order = conn.execute(
        sa.text("SELECT COALESCE(MAX(order_number), :offset) FROM permits"),
        {"offset": settings.ORDER_NUMBER_OFFSET},
    ).scalar()
    start_at = int(max_order) + 1

    op.execute(f"CREATE SEQUENCE IF NOT EXISTS {SEQUENCE_NAME} START WITH {start_at}")
    op.execute(f"ALTER SEQUENCE {SEQUENCE_NAME} OWNED BY permits.order_number")
    op.alter_column(
        "permits",
        "order_number",
        server_default=sa.text(f"nextval('{SEQUENCE_NAME}')"),
    )


def downgrade() -> None:
    op.alter_column("permits", "order_number", server_default=None)
    op.execute(f"DROP SEQUENCE IF EXISTS {SEQUENCE_NAME}")
    op.drop_index("idx_permits_order_number", table_name="permits")
    op.drop_constraint("uq_permits_order_number", "permits", type_="unique")
    op.drop_column("permits", "order_number")
