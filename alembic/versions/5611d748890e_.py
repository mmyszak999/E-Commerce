"""empty message

Revision ID: 5611d748890e
Revises: 
Create Date: 2024-02-15 15:12:35.343951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5611d748890e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=75), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('product',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=75), nullable=False),
    sa.Column('price', sa.Numeric(), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=75), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_staff', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('cart',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('category_product_association_table',
    sa.Column('category_id', sa.String(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade')
    )
    op.create_table('order',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('order_accepted', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('payment_accepted', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('being_delivered', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('received', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('product_inventory',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('sold', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user_address',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=False),
    sa.Column('state', sa.String(length=100), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('postal_code', sa.String(length=50), nullable=False),
    sa.Column('street', sa.String(length=50), nullable=True),
    sa.Column('house_number', sa.String(length=50), nullable=False),
    sa.Column('apartment_number', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('cart_item',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('cart_id', sa.String(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('order_item',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('order_id', sa.String(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('order_product_association_table',
    sa.Column('order_id', sa.String(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_product_association_table')
    op.drop_table('order_item')
    op.drop_table('cart_item')
    op.drop_table('user_address')
    op.drop_table('product_inventory')
    op.drop_table('order')
    op.drop_table('category_product_association_table')
    op.drop_table('cart')
    op.drop_table('user')
    op.drop_table('product')
    op.drop_table('category')
    # ### end Alembic commands ###
