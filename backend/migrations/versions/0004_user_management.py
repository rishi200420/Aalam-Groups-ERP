"""Add distributor management fields to users."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_user_management"
down_revision: Union[str, None] = "0003_product_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("employee_id", sa.String(40), nullable=True))
    op.add_column("users", sa.Column("distributor_code", sa.String(40), nullable=True))
    op.add_column("users", sa.Column("territory", sa.String(120), nullable=True))
    op.add_column("users", sa.Column("brand", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("joining_date", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("profile_image_url", sa.Text(), nullable=True))
    op.add_column(
    "users",
    sa.Column(
        "created_by",
        sa.String(36),
        sa.ForeignKey("users.id"),
        nullable=True,
    ),
)
    # SQLite can't ALTER TABLE ... ADD CONSTRAINT directly; batch mode rebuilds the
    # table under the hood so these constraints apply on every supported dialect,
    # including a completely fresh SQLite database (not just Postgres).
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_employee_id", ["employee_id"])
        batch_op.create_unique_constraint("uq_users_distributor_code", ["distributor_code"])
    op.create_index("ix_users_territory", "users", ["territory"])


def downgrade() -> None:
    op.drop_index("ix_users_territory", table_name="users")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_distributor_code", type_="unique")
        batch_op.drop_constraint("uq_users_employee_id", type_="unique")
    op.drop_column("users", "created_by")
    op.drop_column("users", "profile_image_url")
    op.drop_column("users", "joining_date")
    op.drop_column("users", "brand")
    op.drop_column("users", "territory")
    op.drop_column("users", "distributor_code")
    op.drop_column("users", "employee_id")
