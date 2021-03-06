"""empty message

Revision ID: 99706293854c
Revises: f748973e0bff
Create Date: 2021-05-08 03:11:08.600231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99706293854c'
down_revision = 'f748973e0bff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_section')
    with op.batch_alter_table('section', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_section_slug'), ['slug'])

    with op.batch_alter_table('theme', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_theme_slug'), ['slug'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('theme', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_theme_slug'), type_='unique')
        batch_op.drop_column('slug')

    with op.batch_alter_table('section', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_section_slug'), type_='unique')
        batch_op.drop_column('slug')

    op.create_table('_alembic_tmp_section',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('slug', sa.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_section'),
    sa.UniqueConstraint('name', name='uq_section_name'),
    sa.UniqueConstraint('slug', name='uq_section_slug')
    )
    # ### end Alembic commands ###
