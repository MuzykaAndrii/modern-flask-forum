"""empty message

Revision ID: 29ed5fc010fc
Revises: 66df75833aab
Create Date: 2021-05-14 03:04:05.280456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29ed5fc010fc'
down_revision = '66df75833aab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_tag_slug'), ['slug'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_tag_slug'), type_='unique')
        batch_op.drop_column('slug')

    # ### end Alembic commands ###