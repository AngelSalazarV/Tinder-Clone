"""empty message

Revision ID: 03dfbe610752
Revises: 66d48b81235e
Create Date: 2024-09-18 21:40:24.093603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03dfbe610752'
down_revision = '66d48b81235e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_from_id', sa.Integer(), nullable=False),
    sa.Column('user_to_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_from_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_to_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user1_id', sa.Integer(), nullable=False),
    sa.Column('user2_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user1_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    op.drop_table('like')
    # ### end Alembic commands ###
