"""init

Revision ID: df3e56ce4d5f
Revises: 
Create Date: 2019-12-11 16:17:17.690116

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'df3e56ce4d5f'
down_revision = None
branch_labels = None
depends_on = None

roles = sa.Enum('group', 'lecturer', name='roles')


def upgrade():
    op.create_table(
        'calendars',
        sa.Column('_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', roles, nullable=False),
        sa.Column('last_update', sa.DateTime(), nullable=False),
        sa.Column('last_use', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('_id'),
        sa.UniqueConstraint('_id')
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('calendars')
    roles.drop(op.get_bind())
    # ### end Alembic commands ###
