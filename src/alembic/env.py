import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adiciona o caminho src/ no sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importa Base do seu projeto
from rmtpark_api.database.banco_dados import Base
from rmtpark_api.database import modelos  # importa para registrar os modelos

# Config do Alembic
config = context.config

# Interpretar config do logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
