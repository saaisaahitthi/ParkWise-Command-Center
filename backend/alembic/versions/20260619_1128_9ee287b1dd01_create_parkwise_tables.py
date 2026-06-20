"""create parkwise tables

Revision ID: 9ee287b1dd01
Revises:
Create Date: 2026-06-19 11:28:39.253343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

revision: str = "9ee287b1dd01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
    "hotspots",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("cluster_label", sa.Integer(), nullable=False, comment="DBSCAN cluster label (≥0; -1 noise rows excluded)"),
    sa.Column("hotspot_name", sa.String(length=256), nullable=True, comment="Human-readable label, derived from dominant junction name"),
    sa.Column("zone_id", sa.String(length=64), nullable=True, comment="Optional administrative zone identifier"),
    sa.Column("centroid", geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry", nullable=False), nullable=False, comment="Geographic centroid of the cluster (lon, lat)"),
    sa.Column("convex_hull", geoalchemy2.types.Geometry(geometry_type="POLYGON", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True, comment="Convex hull bounding the violation points in the cluster"),
    sa.Column("centroid_lat", sa.Float(), nullable=False, comment="Redundant lat for non-spatial queries"),
    sa.Column("centroid_lon", sa.Float(), nullable=False, comment="Redundant lon for non-spatial queries"),
    sa.Column("radius_m", sa.Float(), nullable=True, comment="Approximate cluster radius in metres"),
    sa.Column("total_violations", sa.Integer(), nullable=False, comment="Total violation count in this cluster"),
    sa.Column("unique_dates", sa.Integer(), nullable=True, comment="Number of distinct dates with violations"),
    sa.Column("dominant_violation_type", sa.String(length=128), nullable=True, comment="Most frequent violation type in this cluster"),
    sa.Column("dominant_vehicle_category", sa.String(length=64), nullable=True),
    sa.Column("avg_fine_amount", sa.Float(), nullable=True),
    sa.Column("violation_density", sa.Float(), nullable=True, comment="Violations per km² within the cluster footprint"),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_hotspots")),
    sa.UniqueConstraint("cluster_label", name=op.f("uq_hotspots_cluster_label")),
    )
    op.create_index("ix_hotspots_centroid_gist", "hotspots", ["centroid"], unique=False, postgresql_using="gist")
    op.create_index("ix_hotspots_hull_gist", "hotspots", ["convex_hull"], unique=False, postgresql_using="gist")
    op.create_index("ix_hotspots_total_violations", "hotspots", ["total_violations"], unique=False)
    op.create_index("ix_hotspots_zone", "hotspots", ["zone_id"], unique=False)
    op.create_index(op.f("ix_hotspots_zone_id"), "hotspots", ["zone_id"], unique=False)


    op.create_table(
    "violations",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("violation_id", sa.String(length=64), nullable=True, comment="Original violation ID from dataset, if present"),
    sa.Column("violation_type", sa.String(length=128), nullable=False, comment="Category of parking violation"),
    sa.Column("violation_code", sa.String(length=32), nullable=True, comment="Enforcement code, if available"),
    sa.Column("vehicle_category", sa.String(length=64), nullable=True, comment="Two-wheeler, car, truck, etc."),
    sa.Column("vehicle_type", sa.String(length=64), nullable=True),
    sa.Column("violation_date", sa.DateTime(), nullable=False, comment="UTC datetime of the violation"),
    sa.Column("hour_of_day", sa.Integer(), nullable=True, comment="Derived: 0–23, stored for query performance"),
    sa.Column("day_of_week", sa.Integer(), nullable=True, comment="Derived: 0=Monday … 6=Sunday"),
    sa.Column("week_number", sa.Integer(), nullable=True, comment="ISO week number"),
    sa.Column("month", sa.Integer(), nullable=True, comment="1–12"),
    sa.Column("latitude", sa.Float(), nullable=True),
    sa.Column("longitude", sa.Float(), nullable=True),
    sa.Column("location", geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True, comment="PostGIS POINT geometry (lon, lat) — populated during ingestion"),
    sa.Column("junction_name", sa.String(length=256), nullable=True, comment="Named junction from dataset; 49.5% may be NULL"),
    sa.Column("ward", sa.String(length=128), nullable=True),
    sa.Column("zone", sa.String(length=128), nullable=True),
    sa.Column("address_raw", sa.Text(), nullable=True),
    sa.Column("fine_amount", sa.Float(), nullable=True),
    sa.Column("is_paid", sa.Boolean(), nullable=True),
    sa.Column("data_source", sa.String(length=64), nullable=False),
    sa.Column("ingested_at", sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_violations")),
    )
    op.create_index("ix_violations_date_type", "violations", ["violation_date", "violation_type"], unique=False)
    op.create_index("ix_violations_junction_date", "violations", ["junction_name", "violation_date"], unique=False)
    op.create_index(op.f("ix_violations_junction_name"), "violations", ["junction_name"], unique=False)
    op.create_index("ix_violations_location_gist", "violations", ["location"], unique=False, postgresql_using="gist")
    op.create_index(op.f("ix_violations_violation_date"), "violations", ["violation_date"], unique=False)
    op.create_index(op.f("ix_violations_violation_id"), "violations", ["violation_id"], unique=False)

    op.create_table(
    "eis_scores",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=False),
    sa.Column("computed_for_date", sa.DateTime(), nullable=False, comment="The date range this EIS was computed over"),
    sa.Column("frequency_score", sa.Float(), nullable=False, comment="Percentile rank of violation frequency"),
    sa.Column("recurrence_score", sa.Float(), nullable=False, comment="Percentile rank of recurrence within dataset"),
    sa.Column("density_score", sa.Float(), nullable=False, comment="Percentile rank of spatial density"),
    sa.Column("temporal_risk_score", sa.Float(), nullable=False, comment="Percentile rank of peak-window overlap"),
    sa.Column("severity_norm", sa.Float(), nullable=False, comment="Average normalised severity of violations [0,1]"),
    sa.Column("exposure_score", sa.Float(), nullable=False, comment="Weighted sum of frequency/recurrence/density/temporal"),
    sa.Column("severity_multiplier", sa.Float(), nullable=False, comment="0.6 + (0.8 × severity_norm)"),
    sa.Column("eis_score", sa.Float(), nullable=False, comment="Final EIS score, 0–100"),
    sa.Column("risk_category", sa.String(length=16), nullable=False, comment="Low | Medium | High | Critical"),
    sa.Column("rank", sa.Integer(), nullable=True, comment="Rank among all hotspots (1 = most urgent)"),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_eis_scores_hotspot_id_hotspots"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_eis_scores")),
    )
    op.create_index("ix_eis_hotspot_date", "eis_scores", ["hotspot_id", "computed_for_date"], unique=False)
    op.create_index("ix_eis_risk_cat", "eis_scores", ["risk_category"], unique=False)
    op.create_index("ix_eis_score_desc", "eis_scores", ["eis_score"], unique=False)
    op.create_index(op.f("ix_eis_scores_hotspot_id"), "eis_scores", ["hotspot_id"], unique=False)

    op.create_table(
    "enriched_violations",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("violation_id", sa.BigInteger(), nullable=False, comment="1:1 link back to the raw violation"),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=True, comment="Assigned DBSCAN cluster; NULL if noise point"),
    sa.Column("severity_score", sa.Float(), nullable=False, comment="Normalised [0,1] violation severity"),
    sa.Column("is_recurrence", sa.Boolean(), nullable=False, comment="True if location had violations in prior 7 days"),
    sa.Column("temporal_flag", sa.Boolean(), nullable=False, comment="True if violation falls within a peak time window"),
    sa.Column("cluster_label", sa.Integer(), nullable=True, comment="Raw DBSCAN label (-1 = noise)"),
    sa.Column("distance_to_core", sa.Float(), nullable=True, comment="Distance to cluster core point (degrees)"),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True, comment="Identifier for the pipeline run that produced this row"),
    sa.Column("processed_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_enriched_violations_hotspot_id_hotspots"), ondelete="SET NULL"),
    sa.ForeignKeyConstraint(["violation_id"], ["violations.id"], name=op.f("fk_enriched_violations_violation_id_violations"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_enriched_violations")),
    )
    op.create_index("ix_enriched_hotspot_severity", "enriched_violations", ["hotspot_id", "severity_score"], unique=False)
    op.create_index(op.f("ix_enriched_violations_hotspot_id"), "enriched_violations", ["hotspot_id"], unique=False)
    op.create_index(op.f("ix_enriched_violations_violation_id"), "enriched_violations", ["violation_id"], unique=True)

    op.create_table(
    "forecasts",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=False),
    sa.Column("forecast_date", sa.DateTime(), nullable=False, comment="The future date being predicted"),
    sa.Column("horizon_days", sa.Integer(), nullable=False, comment="How many days ahead this forecast is for"),
    sa.Column("predicted_eis", sa.Float(), nullable=False, comment="Predicted EIS score for the forecast date"),
    sa.Column("predicted_risk_category", sa.String(length=16), nullable=False, comment="Low | Medium | High | Critical"),
    sa.Column("confidence_lower", sa.Float(), nullable=True, comment="Lower bound of prediction interval"),
    sa.Column("confidence_upper", sa.Float(), nullable=True, comment="Upper bound of prediction interval"),
    sa.Column("shap_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="SHAP feature contributions as {feature: value} dict"),
    sa.Column("top_features", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Top 5 contributing features [{'feature':..,'value':..}]"),
    sa.Column("model_version", sa.String(length=32), nullable=True),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_forecasts_hotspot_id_hotspots"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_forecasts")),
    sa.UniqueConstraint("hotspot_id", "forecast_date", "horizon_days", name="uq_forecast_hotspot_date_horizon"),
    )
    op.create_index("ix_forecast_date_risk", "forecasts", ["forecast_date", "predicted_risk_category"], unique=False)
    op.create_index(op.f("ix_forecasts_forecast_date"), "forecasts", ["forecast_date"], unique=False)
    op.create_index(op.f("ix_forecasts_hotspot_id"), "forecasts", ["hotspot_id"], unique=False)

    op.create_table(
    "patrol_routes",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=True, comment="Primary (first) hotspot in this route; NULL for a multi-zone route"),
    sa.Column("route_name", sa.String(length=128), nullable=True, comment="E.g. 'Zone A – Morning Shift'"),
    sa.Column("shift_label", sa.String(length=32), nullable=True, comment="Morning | Afternoon | Evening | Night"),
    sa.Column("officer_count", sa.Integer(), nullable=False),
    sa.Column("route_geometry", geoalchemy2.types.Geometry(geometry_type="LINESTRING", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True, comment="Full road-network path as a LINESTRING"),
    sa.Column("stops_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment="Ordered list of stop objects (see docstring)"),
    sa.Column("total_distance_km", sa.Float(), nullable=True),
    sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
    sa.Column("hotspots_covered", sa.Integer(), nullable=True, comment="Number of distinct hotspots in this route"),
    sa.Column("total_eis_covered", sa.Float(), nullable=True, comment="Sum of EIS scores for all covered hotspots"),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_patrol_routes_hotspot_id_hotspots"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_patrol_routes")),
    )
    op.create_index("ix_patrol_routes_geometry_gist", "patrol_routes", ["route_geometry"], unique=False, postgresql_using="gist")
    op.create_index(op.f("ix_patrol_routes_hotspot_id"), "patrol_routes", ["hotspot_id"], unique=False)
    op.create_index("ix_patrol_routes_shift", "patrol_routes", ["shift_label"], unique=False)

    op.create_table(
    "peak_windows",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=True, comment="NULL means the window is city-wide (not hotspot-specific)"),
    sa.Column("day_of_week", sa.Integer(), nullable=True, comment="0=Monday … 6=Sunday; NULL means all days"),
    sa.Column("hour_of_day", sa.Integer(), nullable=True, comment="0–23; NULL means all hours"),
    sa.Column("window_label", sa.String(length=64), nullable=True, comment="E.g. 'Morning Rush', 'Lunch', 'Evening Rush'"),
    sa.Column("violation_count", sa.Integer(), nullable=False),
    sa.Column("avg_violations", sa.Float(), nullable=True, comment="Average violations per occurrence of this window"),
    sa.Column("pct_of_total", sa.Float(), nullable=True, comment="Percentage of total violations in this window"),
    sa.Column("recommended_start_hour", sa.Integer(), nullable=True),
    sa.Column("recommended_end_hour", sa.Integer(), nullable=True),
    sa.Column("enforcement_priority", sa.String(length=16), nullable=True, comment="Low | Medium | High | Critical"),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_peak_windows_hotspot_id_hotspots"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_peak_windows")),
    )
    op.create_index("ix_peak_windows_hotspot_day_hour", "peak_windows", ["hotspot_id", "day_of_week", "hour_of_day"], unique=False)
    op.create_index(op.f("ix_peak_windows_hotspot_id"), "peak_windows", ["hotspot_id"], unique=False)

    op.create_table(
    "allocations",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column("hotspot_id", sa.BigInteger(), nullable=False),
    sa.Column("eis_score_id", sa.BigInteger(), nullable=True),
    sa.Column("officers_allocated", sa.Integer(), nullable=False, comment="Number of officers recommended for this hotspot"),
    sa.Column("allocation_fraction", sa.Float(), nullable=False, comment="Fraction of total available officers assigned here"),
    sa.Column("priority_rank", sa.Integer(), nullable=False, comment="Rank in the deployment priority order"),
    sa.Column("deployment_window", sa.String(length=64), nullable=True, comment="Recommended time window, e.g. '07:00–10:00'"),
    sa.Column("total_officers_available", sa.Integer(), nullable=False, comment="Total officer count used for this calculation"),
    sa.Column("eis_snapshot", sa.Float(), nullable=True, comment="EIS value at time of allocation"),
    sa.Column("risk_category", sa.String(length=16), nullable=True),
    sa.Column("allocation_date", sa.DateTime(), nullable=False),
    sa.Column("pipeline_run_id", sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(["eis_score_id"], ["eis_scores.id"], name=op.f("fk_allocations_eis_score_id_eis_scores"), ondelete="SET NULL"),
    sa.ForeignKeyConstraint(["hotspot_id"], ["hotspots.id"], name=op.f("fk_allocations_hotspot_id_hotspots"), ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_allocations")),
    )
    op.create_index("ix_alloc_hotspot_date", "allocations", ["hotspot_id", "allocation_date"], unique=False)
    op.create_index("ix_alloc_priority", "allocations", ["priority_rank"], unique=False)
    op.create_index(op.f("ix_allocations_hotspot_id"), "allocations", ["hotspot_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_allocations_hotspot_id"), table_name="allocations")
    op.drop_index("ix_alloc_priority", table_name="allocations")
    op.drop_index("ix_alloc_hotspot_date", table_name="allocations")
    op.drop_table("allocations")


    op.drop_index(op.f("ix_peak_windows_hotspot_id"), table_name="peak_windows")
    op.drop_index("ix_peak_windows_hotspot_day_hour", table_name="peak_windows")
    op.drop_table("peak_windows")

    op.drop_index("ix_patrol_routes_shift", table_name="patrol_routes")
    op.drop_index(op.f("ix_patrol_routes_hotspot_id"), table_name="patrol_routes")
    op.drop_index("ix_patrol_routes_geometry_gist", table_name="patrol_routes", postgresql_using="gist")
    op.drop_table("patrol_routes")

    op.drop_index(op.f("ix_forecasts_hotspot_id"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_forecast_date"), table_name="forecasts")
    op.drop_index("ix_forecast_date_risk", table_name="forecasts")
    op.drop_table("forecasts")

    op.drop_index(op.f("ix_enriched_violations_violation_id"), table_name="enriched_violations")
    op.drop_index(op.f("ix_enriched_violations_hotspot_id"), table_name="enriched_violations")
    op.drop_index("ix_enriched_hotspot_severity", table_name="enriched_violations")
    op.drop_table("enriched_violations")

    op.drop_index(op.f("ix_eis_scores_hotspot_id"), table_name="eis_scores")
    op.drop_index("ix_eis_score_desc", table_name="eis_scores")
    op.drop_index("ix_eis_risk_cat", table_name="eis_scores")
    op.drop_index("ix_eis_hotspot_date", table_name="eis_scores")
    op.drop_table("eis_scores")

    op.drop_index(op.f("ix_violations_violation_id"), table_name="violations")
    op.drop_index(op.f("ix_violations_violation_date"), table_name="violations")
    op.drop_index("ix_violations_location_gist", table_name="violations", postgresql_using="gist")
    op.drop_index(op.f("ix_violations_junction_name"), table_name="violations")
    op.drop_index("ix_violations_junction_date", table_name="violations")
    op.drop_index("ix_violations_date_type", table_name="violations")
    op.drop_table("violations")

    op.drop_index(op.f("ix_hotspots_zone_id"), table_name="hotspots")
    op.drop_index("ix_hotspots_zone", table_name="hotspots")
    op.drop_index("ix_hotspots_total_violations", table_name="hotspots")
    op.drop_index("ix_hotspots_hull_gist", table_name="hotspots", postgresql_using="gist")
    op.drop_index("ix_hotspots_centroid_gist", table_name="hotspots", postgresql_using="gist")
    op.drop_table("hotspots")

