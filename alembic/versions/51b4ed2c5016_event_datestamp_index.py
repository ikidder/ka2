"""event datestamp index

Revision ID: 51b4ed2c5016
Revises: 0a8017f77dd0
Create Date: 2020-12-26 08:39:21.024046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51b4ed2c5016'
down_revision = '0a8017f77dd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('http_event_datestamp_index', 'event', ['datestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('http_event_datestamp_index', table_name='event')
    # ### end Alembic commands ###
