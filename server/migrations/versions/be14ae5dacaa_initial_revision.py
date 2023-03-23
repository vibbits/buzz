"""Initial revision

Revision ID: be14ae5dacaa
Revises: 
Create Date: 2023-03-23 16:03:13.268688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "be14ae5dacaa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "polls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("active", sa.DateTime(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "poll_options",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poll", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["poll"],
            ["polls.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("votes", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "poll_votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("option", sa.Integer(), nullable=False),
        sa.Column("poll", sa.Integer(), nullable=False),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["option"],
            ["poll_options.id"],
        ),
        sa.ForeignKeyConstraint(
            ["poll"],
            ["polls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "question_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
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
    )


def downgrade() -> None:
    op.drop_table("question_comments")
    op.drop_table("poll_votes")
    op.drop_table("questions")
    op.drop_table("poll_options")
    op.drop_table("users")
    op.drop_table("polls")
