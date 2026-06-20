from __future__ import annotations

from app.ml.forecast.model import ForecastModel


def make_training_data(rows: int = 20):
    X = []
    y = []

    for i in range(rows):
        X.append(
            [
                1.0,
                float(i % 7),
                float((i % 28) + 1),
                1.0,
                0.0,
                float(30 + i),
                50.0,
                40.0,
                60.0,
                70.0,
                50.0,
                55.0,
                1.1,
                2.0,
                float(30 + i),
                float(28 + i),
                2.0,
                3.0,
                5.0,
                1.0,
                1.0,
            ]
        )
        y.append(float(35 + i))

    feature_names = [f"f{i}" for i in range(len(X[0]))]
    return X, y, feature_names


def test_forecast_model_trains_successfully():
    X, y, feature_names = make_training_data()

    model = ForecastModel(prefer_lightgbm=False)
    result = model.fit(X, y, feature_names)

    assert model.is_trained is True
    assert result.train_size > 0
    assert result.validation_size > 0
    assert result.model_type == "sklearn_hist_gradient_boosting"
    assert result.feature_names == feature_names


def test_predict_one_returns_valid_prediction():
    X, y, feature_names = make_training_data()

    model = ForecastModel(prefer_lightgbm=False)
    model.fit(X, y, feature_names)

    prediction = model.predict_one(X[0])

    assert 0.0 <= prediction.predicted_eis <= 100.0
    assert prediction.predicted_risk_category in {"Low", "Medium", "High", "Critical"}
    assert 0.0 <= prediction.confidence <= 1.0
    assert 0.0 <= prediction.confidence_lower <= 100.0
    assert 0.0 <= prediction.confidence_upper <= 100.0


def test_predict_many_returns_same_count():
    X, y, feature_names = make_training_data()

    model = ForecastModel(prefer_lightgbm=False)
    model.fit(X, y, feature_names)

    predictions = model.predict_many(X[:5])

    assert len(predictions) == 5


def test_untrained_model_raises():
    model = ForecastModel(prefer_lightgbm=False)

    try:
        model.predict_one([1.0] * 21)
        assert False
    except RuntimeError:
        assert True


def test_feature_importance_is_json_compatible():
    X, y, feature_names = make_training_data()

    model = ForecastModel(prefer_lightgbm=False)
    model.fit(X, y, feature_names)

    importance = model.get_feature_importance()

    assert isinstance(importance, dict)
    assert set(importance.keys()) == set(feature_names)
    assert all(isinstance(v, float) for v in importance.values())


def test_model_serialization_roundtrip():
    X, y, feature_names = make_training_data()

    model = ForecastModel(prefer_lightgbm=False)
    model.fit(X, y, feature_names)

    payload = model.dumps()
    restored = ForecastModel.loads(payload)

    assert restored.is_trained is True
    assert restored.model_version == model.model_version
    assert restored.feature_names == model.feature_names