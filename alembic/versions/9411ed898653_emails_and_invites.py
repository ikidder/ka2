"""emails and invites

Revision ID: 9411ed898653
Revises: 8e10727540ad
Create Date: 2020-11-20 11:47:09.496776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9411ed898653'
down_revision = '8e10727540ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_user_id', sa.Integer(), nullable=False),
    sa.Column('to_email', sa.String(length=120), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('responded', sa.DateTime(), nullable=True),
    sa.Column('user_created', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_created'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invite')
    # ### end Alembic commands ###