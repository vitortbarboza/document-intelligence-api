from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command
from app.db.database import PROJECT_ROOT


# Build an Alembic configuration pointing to a temporary SQLite database.
def make_alembic_config(database_path):
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite:///{database_path.as_posix()}",
    )

    return config


# Verify that migrations apply cleanly, match the ORM models, and can be reverted.
def test_migrations_upgrade_check_and_downgrade(tmp_path):
    database_path = tmp_path / "migrations.db"
    config = make_alembic_config(database_path)
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")

    try:
        command.upgrade(config, "head")

        assert "documents" in inspect(engine).get_table_names()

        # Fails if the models changed without a corresponding migration.
        command.check(config)

        command.downgrade(config, "base")

        assert "documents" not in inspect(engine).get_table_names()
    finally:
        engine.dispose()


# Verify that the latest migration enables SQLite AUTOINCREMENT.
# Without it, SQLite may reuse the ID of the most recently deleted document.
def test_migrations_enable_sqlite_autoincrement(tmp_path):
    database_path = tmp_path / "migrations.db"
    command.upgrade(make_alembic_config(database_path), "head")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")

    try:
        with engine.connect() as connection:
            table_sql = connection.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE name = 'documents'"
            ).scalar_one()
    finally:
        engine.dispose()

    assert "AUTOINCREMENT" in table_sql
