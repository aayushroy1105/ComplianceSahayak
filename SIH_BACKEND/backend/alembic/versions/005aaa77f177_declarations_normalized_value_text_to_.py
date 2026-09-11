"""declarations_normalized_value_text_to_jsonb

Revision ID: 005aaa77f177
Revises: 1d605ea4b436
Create Date: 2026-09-11

Minimal migration: converts declarations.normalized_value from Text to JSONB.
Existing text values are converted to JSON strings via to_jsonb().
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005aaa77f177'
down_revision: Union[str, None] = '1d605ea4b436'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'declarations',
        'normalized_value',
        type_=postgresql.JSONB,
        postgresql_using='to_jsonb(normalized_value)',
        existing_type=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'declarations',
        'normalized_value',
        type_=sa.Text(),
        postgresql_using='normalized_value::text',
        existing_type=postgresql.JSONB,
        existing_nullable=True,
    )
