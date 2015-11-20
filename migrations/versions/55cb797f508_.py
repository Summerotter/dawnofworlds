"""empty message

Revision ID: 55cb797f508
Revises: None
Create Date: 2015-09-07 22:11:14.697385

"""

# revision identifiers, used by Alembic.
revision = '55cb797f508'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_roles_default', 'roles', ['default'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('about_me', sa.Text(), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('avatar_hash', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_table('world',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('turn_of_age', sa.Integer(), nullable=True),
    sa.Column('total_turns', sa.Integer(), nullable=True),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('owner', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_world_age', 'world', ['age'], unique=False)
    op.create_index('ix_world_name', 'world', ['name'], unique=True)
    op.create_index('ix_world_total_turns', 'world', ['total_turns'], unique=False)
    op.create_index('ix_world_turn_of_age', 'world', ['turn_of_age'], unique=False)
    op.create_table('follows',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_timestamp', 'posts', ['timestamp'], unique=False)
    op.create_table('turn_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('world_id', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('player', sa.Integer(), nullable=True),
    sa.Column('actions', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['player'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world_id'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('world_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('text', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('race',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('world_id', sa.Integer(), nullable=True),
    sa.Column('culture_name', sa.String(length=128), nullable=True),
    sa.Column('race_name', sa.String(length=64), nullable=True),
    sa.Column('map_color', sa.Integer(), nullable=True),
    sa.Column('alignment', sa.Integer(), nullable=True),
    sa.Column('creator', sa.Integer(), nullable=True),
    sa.Column('abs_turn_made', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('subrace', sa.Integer(), nullable=True),
    sa.Column('religion', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world_id'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_race_culture_name', 'race', ['culture_name'], unique=False)
    op.create_table('player_worlds',
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('world_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world_id'], ['world.id'], )
    )
    op.create_table('power_points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('bonus', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('worldmap',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('race', sa.Integer(), nullable=True),
    sa.Column('letter_coord', sa.Integer(), nullable=True),
    sa.Column('number_coord', sa.Integer(), nullable=True),
    sa.Column('terrain', sa.String(length=16), nullable=True),
    sa.Column('image', sa.String(length=16), nullable=True),
    sa.ForeignKeyConstraint(['race'], ['race.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('race_advances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('race_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['race_id'], ['race.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=128), nullable=True),
    sa.Column('is_alive', sa.Integer(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('founding_culture', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['founding_culture'], ['race.id'], ),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('avatars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('birthed_race', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['location'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('event_info', sa.String(length=128), nullable=True),
    sa.Column('played_by', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['played_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('world_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('built_by', sa.Integer(), nullable=True),
    sa.Column('owned_by', sa.Integer(), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('alignment', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('turn_built', sa.Integer(), nullable=True),
    sa.Column('is_alive', sa.Integer(), nullable=True),
    sa.Column('destroyed_in', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['owned_by'], ['race.id'], ),
    sa.ForeignKeyConstraint(['world_id'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bldg_prov',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('built_by', sa.Integer(), nullable=True),
    sa.Column('world_in', sa.Integer(), nullable=True),
    sa.Column('owned_by', sa.Integer(), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('turn_built', sa.Integer(), nullable=True),
    sa.Column('is_alive', sa.Integer(), nullable=True),
    sa.Column('destroyed_in', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['location'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['owned_by'], ['race.id'], ),
    sa.ForeignKeyConstraint(['world_in'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_location',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], )
    )
    op.create_table('order_city',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cityid', sa.Integer(), nullable=True),
    sa.Column('abs_turn', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('entry', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['cityid'], ['city.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('armies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('army', sa.Integer(), nullable=True),
    sa.Column('supported_from', sa.Integer(), nullable=True),
    sa.Column('home_culture', sa.Integer(), nullable=True),
    sa.Column('owner', sa.Integer(), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('world', sa.Integer(), nullable=True),
    sa.Column('home_city', sa.Integer(), nullable=True),
    sa.Column('is_alive', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['home_culture'], ['race.id'], ),
    sa.ForeignKeyConstraint(['location'], ['worldmap.id'], ),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
    sa.ForeignKeyConstraint(['supported_from'], ['city.id'], ),
    sa.ForeignKeyConstraint(['world'], ['world.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bldg_city',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.Column('built_in', sa.Integer(), nullable=True),
    sa.Column('age_turn', sa.String(length=64), nullable=True),
    sa.Column('turn_built', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['built_in'], ['city.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city_advances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('city_advances')
    op.drop_table('bldg_city')
    op.drop_table('armies')
    op.drop_table('city_history')
    op.drop_table('order_city')
    op.drop_table('order_location')
    op.drop_table('bldg_prov')
    op.drop_table('city')
    op.drop_table('events')
    op.drop_table('avatars')
    op.drop_table('orders')
    op.drop_table('race_advances')
    op.drop_table('worldmap')
    op.drop_table('power_points')
    op.drop_table('player_worlds')
    op.drop_index('ix_race_culture_name', 'race')
    op.drop_table('race')
    op.drop_table('world_history')
    op.drop_table('turn_log')
    op.drop_index('ix_posts_timestamp', 'posts')
    op.drop_table('posts')
    op.drop_table('follows')
    op.drop_index('ix_world_turn_of_age', 'world')
    op.drop_index('ix_world_total_turns', 'world')
    op.drop_index('ix_world_name', 'world')
    op.drop_index('ix_world_age', 'world')
    op.drop_table('world')
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
    op.drop_index('ix_roles_default', 'roles')
    op.drop_table('roles')
    op.drop_table('order_types')
    ### end Alembic commands ###
