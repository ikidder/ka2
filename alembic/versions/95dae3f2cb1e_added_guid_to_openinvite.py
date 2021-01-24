"""added guid to OpenInvite

Revision ID: 95dae3f2cb1e
Revises: 1a01d9e4a244
Create Date: 2021-01-23 16:34:28.525980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95dae3f2cb1e'
down_revision = '1a01d9e4a244'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('open_invite', sa.Column('guid', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('open_invite', 'guid')
    # ### end Alembic commands ###