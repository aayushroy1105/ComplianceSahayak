"""rename_confirmed_to_locked

Revision ID: b8c2b0b2620b
Revises: 3d4fd18549ce
Create Date: 2026-09-11 14:20:14.799173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8c2b0b2620b'
down_revision: Union[str, Sequence[str], None] = '3d4fd18549ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('check_review_status', 'inspections', type_='check')
    op.execute("UPDATE inspections SET review_status = 'LOCKED' WHERE review_status = 'CONFIRMED'")
    op.create_check_constraint(
        'check_review_status', 
        'inspections', 
        "review_status IN ('NOT_REQUIRED', 'PENDING', 'REVIEWED', 'LOCKED', 'REJECTED')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('check_review_status', 'inspections', type_='check')
    op.execute("UPDATE inspections SET review_status = 'CONFIRMED' WHERE review_status = 'LOCKED'")
    op.create_check_constraint(
        'check_review_status', 
        'inspections', 
        "review_status IN ('NOT_REQUIRED', 'PENDING', 'REVIEWED', 'CONFIRMED', 'REJECTED')"
    )
