" Database connection and setup "
import argparse

from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.config import settings
from app.models import Base, User

engine = create_engine(
    settings.database_uri,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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
    parser.add_argument(
        "-n",
        "--user_name",
        type=str,
        required=False,
        help="Name of the user to operate on",
    )

    args = parser.parse_args()

    admin_engine = create_engine(settings.backup_database_uri, future=True, echo=False)
    admin_session = sessionmaker(bind=admin_engine)

    if args.operation == "list_users":
        table = Table(title="Users")
        table.add_column("id")
        table.add_column("Name")
        table.add_column("Role", justify="right")

        with admin_session() as database:
            for user in database.query(User).all():
                table.add_row(
                    str(user.id), f"{user.first_name} {user.last_name}", user.role
                )

        console = Console()
        console.print(table)
    elif args.operation == "promote_user":
        with admin_session() as database:
            crud.promote(database, args.user)

    elif args.operation == "create_user":
        with admin_session() as database:
            first_name, last_name = args.split(" ", 1)
            crud.create_user(database, args.user, first_name, last_name, None)
