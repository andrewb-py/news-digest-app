"""add submission_id to news_items

Revision ID: b94045854af7
Revises: 614e64fc2d3b
Create Date: 2026-04-24 03:34:08.482202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b94045854af7'
down_revision: Union[str, None] = '614e64fc2d3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
