from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import Settings

LOGGER = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_CONFIG_PATH = BACKEND_DIR / "alembic.ini"
MIGRATIONS_PATH = BACKEND_DIR / "migrations"


def create_alembic_config(settings: Settings) -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(MIGRATIONS_PATH))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.attributes["configure_logger"] = False
    return config


def _generate_revision_if_needed(config: Config, message: str) -> None:
    def process_revision_directives(context, revision, directives):
        if directives and directives[0].upgrade_ops.is_empty():
            LOGGER.info("No schema changes detected; skipping revision generation.")
            directives[:] = []

    config.attributes["process_revision_directives"] = process_revision_directives
    command.revision(config, message=message, autogenerate=True)
    config.attributes.pop("process_revision_directives", None)


def run_migrations_on_startup(settings: Settings) -> None:
    if not settings.auto_run_migrations:
        LOGGER.info("Automatic migrations disabled; skipping upgrade.")
        return

    config = create_alembic_config(settings)

    autogenerate = settings.should_autogenerate_migrations
    if autogenerate:
        LOGGER.info("Autogenerating migrations based on current models.")
        _generate_revision_if_needed(config, "Auto generated migration")
    else:
        LOGGER.info("Autogenerate disabled; applying existing migrations only.")

    command.upgrade(config, "head")
