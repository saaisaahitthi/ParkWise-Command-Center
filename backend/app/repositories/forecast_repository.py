from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.analytics import EISScore, Forecast


class ForecastRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_historical_eis_scores(
        self,
        hotspot_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[EISScore]:
        query = self.db.query(EISScore)

        if hotspot_id is not None:
            query = query.filter(EISScore.hotspot_id == hotspot_id)

        if start_date is not None:
            query = query.filter(EISScore.computed_for_date >= start_date)

        if end_date is not None:
            query = query.filter(EISScore.computed_for_date <= end_date)

        query = query.order_by(EISScore.hotspot_id.asc(), EISScore.computed_for_date.asc())

        if limit is not None:
            query = query.limit(limit)

        return list(query.all())

    def count_eis_scores(self, hotspot_id: Optional[int] = None) -> int:
        query = self.db.query(func.count(EISScore.id))
        if hotspot_id is not None:
            query = query.filter(EISScore.hotspot_id == hotspot_id)
        return int(query.scalar() or 0)

    def create_forecast(
        self,
        hotspot_id: int,
        forecast_date: datetime,
        horizon_days: int,
        predicted_eis: float,
        predicted_risk_category: str,
        confidence_lower: Optional[float],
        confidence_upper: Optional[float],
        shap_values: Optional[Dict[str, Any]],
        top_features: Optional[Dict[str, Any]],
        model_version: str,
        pipeline_run_id: Optional[str] = None,
    ) -> Forecast:
        forecast = Forecast(
            hotspot_id=hotspot_id,
            forecast_date=forecast_date,
            horizon_days=horizon_days,
            predicted_eis=predicted_eis,
            predicted_risk_category=predicted_risk_category,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            shap_values=shap_values,
            top_features=top_features,
            model_version=model_version,
            pipeline_run_id=pipeline_run_id,
        )

        self.db.add(forecast)
        self.db.flush()
        return forecast

    def bulk_create_forecasts(
        self,
        forecast_rows: Sequence[Dict[str, Any]],
        commit: bool = False,
    ) -> List[Forecast]:
        created = [
            Forecast(
                hotspot_id=row["hotspot_id"],
                forecast_date=row["forecast_date"],
                horizon_days=row["horizon_days"],
                predicted_eis=row["predicted_eis"],
                predicted_risk_category=row["predicted_risk_category"],
                confidence_lower=row.get("confidence_lower"),
                confidence_upper=row.get("confidence_upper"),
                shap_values=row.get("shap_values"),
                top_features=row.get("top_features"),
                model_version=row.get("model_version", "forecast-v1"),
                pipeline_run_id=row.get("pipeline_run_id"),
            )
            for row in forecast_rows
        ]
        self.db.add_all(created)
        self.db.flush()

        if commit:
            self.db.commit()

        return created

    def delete_existing_forecasts(
        self,
        horizon_days: Optional[int] = None,
        model_version: Optional[str] = None,
        forecast_date: Optional[datetime] = None,
    ) -> int:
        query = self.db.query(Forecast)

        if horizon_days is not None:
            query = query.filter(Forecast.horizon_days == horizon_days)

        if model_version is not None:
            query = query.filter(Forecast.model_version == model_version)

        if forecast_date is not None:
            query = query.filter(func.date(Forecast.forecast_date) == forecast_date.date())

        deleted = query.delete(synchronize_session=False)
        self.db.flush()
        return int(deleted)

    def list_forecasts(
        self,
        hotspot_id: Optional[int] = None,
        horizon_days: Optional[int] = None,
        risk_category: Optional[str] = None,
        model_version: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Forecast]:
        query = self.db.query(Forecast)

        if hotspot_id is not None:
            query = query.filter(Forecast.hotspot_id == hotspot_id)

        if horizon_days is not None:
            query = query.filter(Forecast.horizon_days == horizon_days)

        if risk_category is not None:
            query = query.filter(Forecast.predicted_risk_category == risk_category)

        if model_version is not None:
            query = query.filter(Forecast.model_version == model_version)

        return list(
            query.order_by(desc(Forecast.forecast_date), desc(Forecast.predicted_eis))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_top_forecasts(
        self,
        limit: int = 20,
        horizon_days: Optional[int] = None,
        risk_categories: Optional[Sequence[str]] = None,
    ) -> List[Forecast]:
        query = self.db.query(Forecast)

        if horizon_days is not None:
            query = query.filter(Forecast.horizon_days == horizon_days)

        if risk_categories:
            query = query.filter(Forecast.predicted_risk_category.in_(list(risk_categories)))

        return list(
            query.order_by(desc(Forecast.predicted_eis), desc(Forecast.forecast_date))
            .limit(limit)
            .all()
        )

    def get_hotspot_forecasts(
        self,
        hotspot_id: int,
        horizon_days: Optional[int] = None,
        limit: int = 30,
    ) -> List[Forecast]:
        return self.list_forecasts(
            hotspot_id=hotspot_id,
            horizon_days=horizon_days,
            limit=limit,
            offset=0,
        )

    def get_summary(self) -> Dict[str, Any]:
        total = self.db.query(func.count(Forecast.id)).scalar() or 0

        avg_eis = self.db.query(func.avg(Forecast.predicted_eis)).scalar()
        max_eis = self.db.query(func.max(Forecast.predicted_eis)).scalar()

        risk_rows = (
            self.db.query(
                Forecast.predicted_risk_category,
                func.count(Forecast.id),
            )
            .group_by(Forecast.predicted_risk_category)
            .all()
        )

        horizon_rows = (
            self.db.query(
                Forecast.horizon_days,
                func.count(Forecast.id),
            )
            .group_by(Forecast.horizon_days)
            .all()
        )

        latest_generated = self.db.query(func.max(Forecast.created_at)).scalar()

        return {
            "total_forecasts": int(total),
            "average_predicted_eis": float(avg_eis or 0.0),
            "max_predicted_eis": float(max_eis or 0.0),
            "risk_distribution": {
                str(category or "Unknown"): int(count)
                for category, count in risk_rows
            },
            "horizon_distribution": {
                str(horizon): int(count)
                for horizon, count in horizon_rows
            },
            "latest_generated_at": latest_generated,
        }
