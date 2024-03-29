"""tags

Revision ID: f48e9ba61164
Revises: 87d1e8c337e5
Create Date: 2020-12-07 11:42:29.468934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f48e9ba61164'
down_revision = '87d1e8c337e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['kabase.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag_association',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('tagged_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['tagged_id'], ['kabase.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag_association')
    op.drop_table('tag')
    # ### end Alembic commands ###
