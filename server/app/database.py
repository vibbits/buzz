" Database connection and setup "
import argparse

from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.config import settings
from app.models import Base, User

engine = create_engine(
    settings.database_uri,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},
)

Session = sessionmaker(
    bind=engine, future=True, autoflush=False, autocommit=False, expire_on_commit=False
)


def build() -> None:
    "Manually rebuild a fresh database."
    with Session() as database:
        Base.metadata.drop_all(database.get_bind())
        Base.metadata.create_all(database.get_bind())


def admin() -> None:
    "Application/database administration user interface."
    parser = argparse.ArgumentParser(description="Database administration interface")
    parser.add_argument("operation", type=str, help="Database operation")
    parser.add_argument(
        "-u", "--user", type=int, required=False, help="User to operate on"
    )

    args = parser.parse_args()

    if args.operation == "list_users":
        table = Table(title="Users")
        table.add_column("id")
        table.add_column("Name")
        table.add_column("Role", justify="right")

        with Session() as database:
            for user in database.query(User).all():
                table.add_row(
                    str(user.id), f"{user.first_name} {user.last_name}", user.role
                )

        console = Console()
        console.print(table)
    elif args.operation == "promote_user":
        with Session() as database:
            crud.promote(database, args.user)
