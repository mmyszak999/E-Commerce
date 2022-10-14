"""Add a column

Revision ID: ff3378310f1e
Revises: 017727d1afa3
Create Date: 2022-09-27 21:22:12.777781

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'ff3378310f1e'
down_revision = '017727d1afa3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column("id", sa.Integer, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.Unicode(200), nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('birth_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    pass
