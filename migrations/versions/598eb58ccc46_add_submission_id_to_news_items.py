"""add submission_id to news_items"""

from alembic import op
import sqlalchemy as sa

revision = '598eb58ccc46'
down_revision = '676a28d54882'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('news_items', sa.Column('submission_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_news_items_submission_id_news_submissions',
        'news_items',
        'news_submissions',
        ['submission_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # Удаляем внешний ключ
    op.drop_constraint('fk_news_items_submission_id_news_submissions', 'news_items', type_='foreignkey')
    # Удаляем колонку
    op.drop_column('news_items', 'submission_id')