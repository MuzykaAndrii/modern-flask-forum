"""empty message

Revision ID: 6c5bd944fc9a
Revises: 5768ca49c73c
Create Date: 2021-05-11 23:42:32.162367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c5bd944fc9a'
down_revision = '5768ca49c73c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.String(length=120), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_user_website'), ['website'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_user_website'), type_='unique')
        batch_op.drop_column('website')

    # ### end Alembic commands ###