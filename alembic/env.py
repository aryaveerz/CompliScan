import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import application settings and models
from backend.app.core.config import settings
from backend.app.db.base import Base
# Import all models to ensure registration on Base.metadata
import backend.app.models  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata

# Override URL from application settings or CLI x-arguments if available
x_args = context.get_x_argument(as_dictionary=True)
db_url = x_args.get("db_url") or settings.SYNC_DATABASE_URL or settings.DATABASE_URL
if db_url.startswith("sqlite+aiosqlite:"):
    db_url = db_url.replace("sqlite+aiosqlite:", "sqlite:")
elif db_url.startswith("postgresql+asyncpg:"):
    db_url = db_url.replace("postgresql+asyncpg:", "postgresql+psycopg:")
elif db_url.startswith("postgres+asyncpg:"):
    db_url = db_url.replace("postgres+asyncpg:", "postgresql+psycopg:")
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

config.set_section_option(
    config.config_ini_section,
    "sqlalchemy.url",
    db_url.replace("%", "%%"),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
