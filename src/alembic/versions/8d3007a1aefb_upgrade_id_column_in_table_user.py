"""upgrade id column in table user

Revision ID: 8d3007a1aefb
Revises: e0d041f2aa56
Create Date: 2022-09-29 13:13:50.144634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d3007a1aefb'
down_revision = 'e0d041f2aa56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.Unicode(200), nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('birth_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default="false")
        )


def downgrade() -> None:
    pass
