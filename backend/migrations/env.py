"""Alembic environment configuration."""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure the backend directory is on sys.path so app modules can be imported.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app settings to read DATABASE_URL from environment / .env file.
from app.config import get_settings  # noqa: E402

# Import all models so Alembic's autogenerate can detect them.
from app.database import Base  # noqa: E402
from app.models import user, job, candidate, audit  # noqa: E402, F401

settings = get_settings()

# Alembic Config object — gives access to values in alembic.ini.
config = context.config

# Override sqlalchemy.url with the value from app settings so we never
# hard-code credentials in alembic.ini.
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"),
)

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object that autogenerate will compare against the database.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required).

    Emits SQL statements to stdout / a file instead of executing them directly.
    Useful for reviewing or applying migrations manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render the CREATE TYPE statements for SQLAlchemy Enum columns.
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to a live database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Render the CREATE TYPE statements for SQLAlchemy Enum columns.
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
