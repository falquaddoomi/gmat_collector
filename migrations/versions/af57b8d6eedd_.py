"""empty message

Revision ID: af57b8d6eedd
Revises: 97faee265d51
Create Date: 2016-08-24 15:50:48.954883

"""

# revision identifiers, used by Alembic.
revision = 'af57b8d6eedd'
down_revision = '97faee265d51'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('practice', sa.Column('site_practice_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('practice', 'site_practice_id')
    ### end Alembic commands ###
