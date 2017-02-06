from __future__ import with_statement

import sys
import os

from logging.config import fileConfig

from sqlalchemy import MetaData
from sqlalchemy import engine_from_config, pool

PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from alembic import context
from alembic.config import Config

config = Config(PROJECT_FOLDER+"/alembic.ini")
sys.path.append(PROJECT_FOLDER)

import i2b2_schema
import data_catalog_schema

fileConfig(config.config_file_name)


def combine_metadata(*args):
    m = MetaData()
    for metadata in args:
        for t in metadata.tables.values():
            t.tometadata(m)
    return m

target_metadata = combine_metadata(i2b2_schema.Base.metadata, data_catalog_schema.Base.metadata)


def run_migrations_offline():
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
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
