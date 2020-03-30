"""empty message

Revision ID: 3b5d9401907
Revises: None
Create Date: 2019-05-21 02:41:23.341178

"""

# revision identifiers, used by Alembic.
revision = '3b5d9401907'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('title',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('copies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['title_id'], ['title.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taassoc',
    sa.Column('title_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['title_id'], ['title.id'], ),
    sa.PrimaryKeyConstraint('title_id', 'author_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('taassoc')
    op.drop_table('copies')
    op.drop_table('title')
    op.drop_table('author')
    ### end Alembic commands ###