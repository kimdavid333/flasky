"""empty message

Revision ID: 7df2b4c2f274
Revises: 
Create Date: 2021-11-30 11:50:37.220594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7df2b4c2f274'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('information_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inspector', sa.String(), nullable=True),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('serial', sa.String(), nullable=True),
    sa.Column('rpm', sa.Integer(), nullable=True),
    sa.Column('vib1', sa.Boolean(), nullable=True),
    sa.Column('vib2', sa.Boolean(), nullable=True),
    sa.Column('vib3', sa.Boolean(), nullable=True),
    sa.Column('vib4', sa.Boolean(), nullable=True),
    sa.Column('vib5', sa.Boolean(), nullable=True),
    sa.Column('vib6', sa.Boolean(), nullable=True),
    sa.Column('amp1', sa.Boolean(), nullable=True),
    sa.Column('amp2', sa.Boolean(), nullable=True),
    sa.Column('amp3', sa.Boolean(), nullable=True),
    sa.Column('temp1', sa.Boolean(), nullable=True),
    sa.Column('temp2', sa.Boolean(), nullable=True),
    sa.Column('temp3', sa.Boolean(), nullable=True),
    sa.Column('temp4', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
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
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('amp1_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('amp2_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('amp3_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('temp1_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('temp2_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('temp3_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('temp4_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
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
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('vib1_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('vib2_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('vib3_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('vib4_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('vib5_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('vib6_table',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ch_name', sa.String(), nullable=True),
    sa.Column('value', sa.LargeBinary(), nullable=True),
    sa.Column('spec', sa.Integer(), nullable=True),
    sa.Column('sprate', sa.Integer(), nullable=True),
    sa.Column('update_flag', sa.Boolean(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['information_table.id'], ),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_timestamp'), 'posts', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_posts_timestamp'), table_name='posts')
    op.drop_table('posts')
    op.drop_table('vib6_table')
    op.drop_table('vib5_table')
    op.drop_table('vib4_table')
    op.drop_table('vib3_table')
    op.drop_table('vib2_table')
    op.drop_table('vib1_table')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('temp4_table')
    op.drop_table('temp3_table')
    op.drop_table('temp2_table')
    op.drop_table('temp1_table')
    op.drop_table('amp3_table')
    op.drop_table('amp2_table')
    op.drop_table('amp1_table')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('information_table')
    # ### end Alembic commands ###