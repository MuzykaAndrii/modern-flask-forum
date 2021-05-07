"""empty message

Revision ID: cd4fb03cd1ed
Revises: b1175d0cfb54
Create Date: 2021-05-07 04:04:45.018512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd4fb03cd1ed'
down_revision = 'b1175d0cfb54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('discussion_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_comment_discussion_id_discussion'), 'discussion', ['discussion_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_comment_creator_id_user'), 'user', ['creator_id'], ['id'])

    with op.batch_alter_table('discussion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('theme_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_discussion_creator_id_user'), 'user', ['creator_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_discussion_theme_id_theme'), 'theme', ['theme_id'], ['id'])

    with op.batch_alter_table('theme', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_theme_section_id_section'), 'section', ['section_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('theme', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_theme_section_id_section'), type_='foreignkey')
        batch_op.drop_column('section_id')

    with op.batch_alter_table('discussion', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_discussion_theme_id_theme'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_discussion_creator_id_user'), type_='foreignkey')
        batch_op.drop_column('theme_id')
        batch_op.drop_column('creator_id')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_comment_creator_id_user'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_comment_discussion_id_discussion'), type_='foreignkey')
        batch_op.drop_column('discussion_id')
        batch_op.drop_column('creator_id')

    # ### end Alembic commands ###
