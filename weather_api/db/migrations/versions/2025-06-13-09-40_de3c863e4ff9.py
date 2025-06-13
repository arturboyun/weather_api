"""Init.

Revision ID: de3c863e4ff9
Revises:
Create Date: 2025-06-13 09:40:24.192573

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "de3c863e4ff9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    op.create_table(
        "temperatures",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("city", sa.String(), nullable=False, comment="City name"),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_temperatures_city"),
        "temperatures",
        ["city"],
        unique=False,
    )


def downgrade() -> None:
    """Undo the migration."""
    op.drop_index(op.f("ix_temperatures_city"), table_name="temperatures")
    op.drop_table("temperatures")
