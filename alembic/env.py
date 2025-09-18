from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override DB URL from environment if provided
DATABASE_URL = os.getenv("DATABASE_URL")
load_dotenv()  # .env dosyasını yükle
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Import application models so that Base.metadata includes all tables
from app.models.base import Base  # type: ignore
import app.models.user  # noqa: F401
import app.models.organization  # noqa: F401
import app.models.org_user  # noqa: F401
import app.models.address  # noqa: F401
import app.models.vehicle  # noqa: F401
import app.models.load  # noqa: F401
import app.models.offer  # noqa: F401
import app.models.match  # noqa: F401
import app.models.rating  # noqa: F401
import app.models.membership  # noqa: F401

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
