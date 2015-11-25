"""empty message

Revision ID: 10e3eee239
Revises: 1040746be6b
Create Date: 2015-11-25 05:04:54.862754

"""

# revision identifiers, used by Alembic.
revision = '10e3eee239'
down_revision = '1040746be6b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=24), nullable=True),
    sa.Column('power', sa.Float(), nullable=True),
    sa.Column('health', sa.Integer(), nullable=True),
    sa.Column('max_health', sa.Integer(), nullable=True),
    sa.Column('assigned_army', sa.Integer(), nullable=True),
    sa.Column('player', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_army'], ['armies.id'], ),
    sa.ForeignKeyConstraint(['player'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('armies', sa.Column('has_moved', sa.Integer(), nullable=True))
    op.add_column('armies', sa.Column('movement_range', sa.Integer(), nullable=True))
    op.add_column('avatars', sa.Column('has_moved', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('avatars', 'has_moved')
    op.drop_column('armies', 'movement_range')
    op.drop_column('armies', 'has_moved')
    op.drop_table('unit')
    ### end Alembic commands ###
