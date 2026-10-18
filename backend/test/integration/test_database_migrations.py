from alembic import command


def test_migration_match_persistence_models(migrated_database, alembic_config):
    command.check(alembic_config)
