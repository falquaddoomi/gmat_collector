"""empty message

Revision ID: 1da105b7c67f
Revises: None
Create Date: 2016-07-10 20:15:50.195732

"""

# revision identifiers, used by Alembic.
revision = '1da105b7c67f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student', sa.Column('has_contingency', sa.Boolean(), nullable=True))
    op.add_column('student', sa.Column('has_deadline', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student', 'has_deadline')
    op.drop_column('student', 'has_contingency')
    ### end Alembic commands ###
