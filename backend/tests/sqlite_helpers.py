"""SQLite-only table setup for unit tests that must avoid spatial DDL."""

from sqlalchemy.engine import Engine


def create_temporal_test_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE enriched_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE peak_windows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotspot_id BIGINT,
                day_of_week INTEGER,
                hour_of_day INTEGER,
                window_label VARCHAR(64),
                violation_count INTEGER NOT NULL,
                avg_violations FLOAT,
                pct_of_total FLOAT,
                recommended_start_hour INTEGER,
                recommended_end_hour INTEGER,
                enforcement_priority VARCHAR(16),
                pipeline_run_id VARCHAR(64),
                created_at DATETIME NOT NULL
            )
            """
        )


def drop_temporal_test_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS peak_windows")
        connection.exec_driver_sql("DROP TABLE IF EXISTS enriched_violations")
