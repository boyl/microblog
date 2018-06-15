"""followers

Revision ID: 71ad6c4cc416
Revises: 5562168e468f
Create Date: 2018-06-12 01:28:12.943473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71ad6c4cc416'
down_revision = '5562168e468f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
