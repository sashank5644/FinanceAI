"""Database migration utilities."""

import logging
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from utils.db.postgres import engine
from config import settings

logger = logging.getLogger(__name__)


def create_alembic_ini():
    """Create alembic.ini configuration file."""
    alembic_ini_content = f"""
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = {settings.postgres_url}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
    
    with open("alembic.ini", "w") as f:
        f.write(alembic_ini_content)


def init_alembic():
    """Initialize Alembic for migrations."""
    try:
        # Create alembic directory
        import os
        os.makedirs("alembic", exist_ok=True)
        
        # Initialize alembic
        alembic_cfg = Config("alembic.ini")
        command.init(alembic_cfg, "alembic")
        
        logger.info("Alembic initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Alembic: {e}")


def create_migration(message: str):
    """Create a new migration."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message=message)
        logger.info(f"Migration created: {message}")
    except Exception as e:
        logger.error(f"Failed to create migration: {e}")


def run_migrations():
    """Run all pending migrations."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
