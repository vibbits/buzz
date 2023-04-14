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


def upgrade() -> None:
    # Remove duplicates
    op.execute(
        """DELETE FROM poll_votes
WHERE id IN (SELECT pv2.id
              FROM   poll_votes pv2
              WHERE  pv2.id NOT IN (SELECT pv.id
                                    FROM   poll_votes pv
                                    GROUP  BY pv.poll,
                                              pv."user",
                                              pv."option"))"""
    )

    with op.batch_alter_table("poll_votes") as batch_op:
        batch_op.create_unique_constraint(
            "one_vote_per_user_per_option", ["option", "poll", "user"]
        )


def downgrade() -> None:
    with op.batch_alter_table("poll_votes") as batch_op:
        batch_op.drop_constraint("one_vote_per_user_per_option", type_="unique")
