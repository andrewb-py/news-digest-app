from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers
revision = '614e64fc2d3b'
down_revision = '598eb58ccc46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Проверяем, существует ли таблица news_topics
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, "news_topics"):
        op.create_table('news_topics',
            sa.Column('news_id', sa.Integer(), nullable=False),
            sa.Column('topic_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['news_id'], ['news_items.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('news_id', 'topic_id')
        )


def downgrade() -> None:
    op.drop_table('news_topics')