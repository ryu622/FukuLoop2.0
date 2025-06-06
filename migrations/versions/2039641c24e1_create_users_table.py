"""create users table

Revision ID: 2039641c24e1
Revises: eac02c0945a4
Create Date: 2025-04-19 15:55:08.118250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2039641c24e1'
down_revision = 'eac02c0945a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
