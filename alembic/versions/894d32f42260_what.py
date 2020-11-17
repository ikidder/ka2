"""what

Revision ID: 894d32f42260
Revises: 556375204902
Create Date: 2020-11-11 10:23:33.541836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '894d32f42260'
down_revision = '556375204902'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('measure', '_ordinal',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.add_column('score', sa.Column('duration', sa.Integer(), nullable=True, default=0))
    op.execute('UPDATE score SET duration = 0')
    op.alter_column('score', 'duration', nullable=False)
    op.alter_column('score', 'count_favorites',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('score', 'count_plays',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('score', 'count_plays',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('score', 'count_favorites',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('score', 'duration')
    op.alter_column('measure', '_ordinal',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###