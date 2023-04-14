"""Store Q&A votes in seperate table

Revision ID: 5459d0ce6fcb
Revises: 1531bc2cfad4
Create Date: 2023-04-14 17:00:56.436830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5459d0ce6fcb"
down_revision = "1531bc2cfad4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Integer(), nullable=False),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question"],
            ["questions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question", "user", name="one_vote_per_user"),
    )

    with op.batch_alter_table("questions") as batch_op:
        batch_op.drop_column("votes")


def downgrade() -> None:
    with op.batch_alter_table("questions") as batch_op:
        batch_op.add_column(sa.Column("votes", sa.INTEGER(), nullable=False))
    op.drop_table("question_votes")
