"""empty message

Revision ID: 7ee5ea7db88a
Revises: 83cce3b6f8b9
Create Date: 2023-03-18 20:37:10.914589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ee5ea7db88a'
down_revision = '83cce3b6f8b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('association_table_category_id_fkey', 'association_table', type_='foreignkey')
    op.drop_constraint('association_table_product_id_fkey', 'association_table', type_='foreignkey')
    op.create_foreign_key(None, 'association_table', 'category', ['category_id'], ['id'], ondelete='cascade')
    op.create_foreign_key(None, 'association_table', 'product', ['product_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'association_table', type_='foreignkey')
    op.drop_constraint(None, 'association_table', type_='foreignkey')
    op.create_foreign_key('association_table_product_id_fkey', 'association_table', 'product', ['product_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key('association_table_category_id_fkey', 'association_table', 'category', ['category_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###