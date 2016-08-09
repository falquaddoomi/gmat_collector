"""empty message

Revision ID: 640e82a8b51d
Revises: 44b093d395b0
Create Date: 2016-07-21 15:45:09.384710

"""

# revision identifiers, used by Alembic.
revision = '640e82a8b51d'
down_revision = '44b093d395b0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'practice_quiz_index_student_id_key', 'practice', type_='unique')
    op.drop_column('practice', 'quiz_index')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('practice', sa.Column('quiz_index', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_unique_constraint(u'practice_quiz_index_student_id_key', 'practice', ['quiz_index', 'student_id'])
    ### end Alembic commands ###