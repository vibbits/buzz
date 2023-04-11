"""One poll vote per user per poll option

Revision ID: 1531bc2cfad4
Revises: be14ae5dacaa
Create Date: 2023-04-11 09:36:14.752540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1531bc2cfad4"
down_revision = "be14ae5dacaa"
branch_labels = None
depends_on = None


def remove_duplicates(session):
    from app.models import PollVote

    unique = session.query(PollVote.id).group_by(
        PollVote.poll, PollVote.user, PollVote.option
    )

    duplicates = session.query(PollVote).filter(~PollVote.id.in_(unique))
    for dup in duplicates:
        session.delete(dup)
    session.commit()


def upgrade() -> None:
    from app.database import Session

    with Session() as session:
        remove_duplicates(session)

    with op.batch_alter_table("poll_votes") as batch_op:
        batch_op.create_unique_constraint(
            "one_vote_per_user_per_option", ["option", "poll", "user"]
        )


def downgrade() -> None:
    with op.batch_alter_table("poll_votes") as batch_op:
        batch_op.drop_constraint("one_vote_per_user_per_option", type_="unique")
