from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from data import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    build_latest_team_data,
    create_match_features,
    load_matches,
    normalize_team_name,
    prepare_xy,
)


@dataclass
class TrainedWorldCupModel:
    pipeline: Pipeline
    latest_team_data: pd.DataFrame
    train_size: int
    test_size: int
    cutoff_date: str

    @property
    def classes_(self) -> list[str]:
        return list(self.pipeline.classes_)


def _build_calibrated_classifier(base_estimator: RandomForestClassifier) -> CalibratedClassifierCV:
    try:
        return CalibratedClassifierCV(
            estimator=base_estimator,
            method="isotonic",
            cv=3,
        )
    except TypeError:
        return CalibratedClassifierCV(
            base_estimator=base_estimator,
            method="isotonic",
            cv=3,
        )


def build_pipeline(random_state: int = 0) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    base_rf = RandomForestClassifier(
        n_estimators=500,
        max_depth=6,
        min_samples_leaf=10,
        random_state=random_state,
        class_weight="balanced",
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", _build_calibrated_classifier(base_rf)),
        ]
    )


def train_model(
    matches: pd.DataFrame | None = None,
    data_dir: str | Path | None = None,
    cutoff_date: str = "2024-01-01",
    random_state: int = 0,
) -> TrainedWorldCupModel:
    if matches is None:
        matches = load_matches(data_dir=data_dir)

    x_train, y_train, x_test, _y_test, train, test = prepare_xy(
        matches,
        cutoff_date=cutoff_date,
    )

    pipeline = build_pipeline(random_state=random_state)
    pipeline.fit(x_train, y_train)

    return TrainedWorldCupModel(
        pipeline=pipeline,
        latest_team_data=build_latest_team_data(matches),
        train_size=len(train),
        test_size=len(test),
        cutoff_date=cutoff_date,
    )


def evaluate_model(
    trained_model: TrainedWorldCupModel,
    matches: pd.DataFrame | None = None,
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    if matches is None:
        matches = load_matches(data_dir=data_dir)

    _x_train, _y_train, x_test, y_test, _train, _test = prepare_xy(
        matches,
        cutoff_date=trained_model.cutoff_date,
    )

    pred = trained_model.pipeline.predict(x_test)
    proba = trained_model.pipeline.predict_proba(x_test)
    proba_df = pd.DataFrame(proba, columns=trained_model.classes_)

    return {
        "train_size": trained_model.train_size,
        "test_size": trained_model.test_size,
        "accuracy": float(accuracy_score(y_test, pred)),
        "log_loss": float(log_loss(y_test, proba, labels=trained_model.classes_)),
        "classification_report": classification_report(y_test, pred, output_dict=True),
        "probability_mean": proba_df.mean().to_dict(),
        "probability_max": proba_df.max().to_dict(),
        "most_likely_class_counts": proba_df.idxmax(axis=1).value_counts().to_dict(),
    }


def predict_match_proba(
    trained_model: TrainedWorldCupModel,
    home_team: str,
    away_team: str,
    tournament: str = "FIFA World Cup",
    neutral: int = 1,
) -> dict[str, float | str]:
    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)

    match_df = create_match_features(
        latest_team_data=trained_model.latest_team_data,
        home_team=home_team,
        away_team=away_team,
        tournament=tournament,
        neutral=neutral,
    )

    probabilities = trained_model.pipeline.predict_proba(match_df)[0]
    proba_dict = dict(zip(trained_model.classes_, probabilities))

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_win": float(proba_dict.get("home_win", 0.0)),
        "draw": float(proba_dict.get("draw", 0.0)),
        "away_win": float(proba_dict.get("away_win", 0.0)),
    }


def display_match_proba(
    trained_model: TrainedWorldCupModel,
    home_team: str,
    away_team: str,
    tournament: str = "FIFA World Cup",
    neutral: int = 1,
) -> dict[str, str]:
    proba = predict_match_proba(
        trained_model=trained_model,
        home_team=home_team,
        away_team=away_team,
        tournament=tournament,
        neutral=neutral,
    )

    return {
        "home_team": str(proba["home_team"]),
        "away_team": str(proba["away_team"]),
        "home_win": f"{float(proba['home_win']) * 100:.2f}%",
        "draw": f"{float(proba['draw']) * 100:.2f}%",
        "away_win": f"{float(proba['away_win']) * 100:.2f}%",
    }


def save_model(trained_model: TrainedWorldCupModel, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(trained_model, output_path)
    return output_path


def load_model(path: str | Path) -> TrainedWorldCupModel:
    return joblib.load(Path(path))


def load_or_train_model(
    model_path: str | Path | None = None,
    data_dir: str | Path | None = None,
    cutoff_date: str = "2024-01-01",
    random_state: int = 0,
) -> TrainedWorldCupModel:
    if model_path is not None and Path(model_path).exists():
        return load_model(model_path)

    trained_model = train_model(
        data_dir=data_dir,
        cutoff_date=cutoff_date,
        random_state=random_state,
    )

    if model_path is not None:
        save_model(trained_model, model_path)

    return trained_model
