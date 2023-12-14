"""create users table

Revision ID: 80720eb81483
Revises: fcde01f05d71
Create Date: 2023-12-14 20:05:54.341253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80720eb81483'
down_revision: Union[str, None] = 'fcde01f05d71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('email', sa.String(), unique=True, nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                              nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_table('users')
    pass
