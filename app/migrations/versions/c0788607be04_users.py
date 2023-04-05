"""users

Revision ID: c0788607be04
Revises: 
Create Date: 2023-04-04 14:29:47.228825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c0788607be04"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=12), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("surname", sa.String(length=50), nullable=False),
        sa.Column("patronymic", sa.String(length=50), nullable=True),
        sa.Column("phone_number", sa.String(length=11), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=50), nullable=False),
        sa.Column(
            "data_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "date_modified",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(
        op.f("ix_users_phone_number"), "users", ["phone_number"], unique=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_phone_number"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###