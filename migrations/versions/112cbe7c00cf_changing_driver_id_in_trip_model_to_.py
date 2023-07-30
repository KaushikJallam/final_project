"""changing driver id in trip model to nullable = true

Revision ID: 112cbe7c00cf
Revises: f5b2de65bd04
Create Date: 2023-07-30 15:08:50.403096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '112cbe7c00cf'
down_revision = 'f5b2de65bd04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trips', schema=None) as batch_op:
        batch_op.alter_column('driver_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trips', schema=None) as batch_op:
        batch_op.alter_column('driver_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###