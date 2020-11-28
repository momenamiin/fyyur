"""empty message

Revision ID: 35002b2ac151
Revises: ee97b061192c
Create Date: 2020-11-22 14:20:48.302665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35002b2ac151'
down_revision = 'ee97b061192c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
