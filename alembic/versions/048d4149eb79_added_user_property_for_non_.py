"""added user property for non transactional emails

Revision ID: 048d4149eb79
Revises: fd3a5b2c9a32
Create Date: 2020-12-25 07:13:18.995309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '048d4149eb79'
down_revision = 'fd3a5b2c9a32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('allow_non_transactional_emails', sa.Boolean(), nullable=True))
    op.execute('UPDATE "user" SET allow_non_transactional_emails = TRUE')
    op.alter_column('user', 'allow_non_transactional_emails', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'allow_non_transactional_emails')
    # ### end Alembic commands ###
