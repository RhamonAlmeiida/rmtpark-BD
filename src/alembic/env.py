from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from alembic import context
import os

config = context.config

# Se estiver usando variável de ambiente
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:senha@localhost:3306/rmtpark")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    ...
