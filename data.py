from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd


DATA_DIR_ENV = "WORLD_CUP_DATA_DIR"
MATCHES_FILENAME = "matches_2012_2026_with_fifa_ranking_clean.csv"
GROUP_MATCHES_FILENAME = "Groups_Matches_corrected_clean.csv"

NUMERIC_FEATURES = [
    "home_fifa_rank",
    "away_fifa_rank",
    "home_fifa_points",
    "away_fifa_points",
    "fifa_rank_diff",
    "fifa_points_diff",
    "neutral",
]

CATEGORICAL_FEATURES = ["tournament"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "result"

REQUIRED_MATCH_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_fifa_rank",
    "away_fifa_rank",
    "home_fifa_points",
    "away_fifa_points",
    "fifa_rank_diff",
    "fifa_points_diff",
    "neutral",
    "tournament",
    "result",
]

REQUIRED_GROUP_COLUMNS = ["group", "home_team", "away_team"]

TEAM_NAME_CORRECTIONS = {
    "USA": "United States",
    "US": "United States",
    "United States of America": "United States",
    "Curacao": "Curaçao",
    "Czechia": "Czech Republic",
    "Czech Repulic": "Czech Republic",
    "Korea Republic": "South Korea",
    "Türkiye": "Turkey",
    "Côte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran",
    "Cabo Verde": "Cape Verde",
    "Cape Verder": "Cape Verde",
    "Congo DR": "DR Congo",
    "Dr Congo": "DR Congo",
    "Columbia": "Colombia",
    "Paragway": "Paraguay",
    "Urugway": "Uruguay",
    "New Zeland": "New Zealand",
    "Egipt": "Egypt",
    "Netherland": "Netherlands",
    "Bosna and Hercegovina": "Bosnia and Herzegovina",
    "Bosnia and Hercegovina": "Bosnia and Herzegovina",
}


def get_data_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir).expanduser().resolve()

    env_data_dir = os.getenv(DATA_DIR_ENV)
    if env_data_dir:
        return Path(env_data_dir).expanduser().resolve()

    return Path(__file__).resolve().parent


def normalize_team_name(team: str) -> str:
    normalized = str(team).strip()
    return TEAM_NAME_CORRECTIONS.get(normalized, normalized)


def validate_columns(df: pd.DataFrame, required_columns: Iterable[str], source: str) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def coerce_neutral_column(series: pd.Series) -> pd.Series:
    mapping = {
        True: 1,
        False: 0,
        "TRUE": 1,
        "FALSE": 0,
        "True": 1,
        "False": 0,
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
        1: 1,
        0: 0,
    }

    coerced = series.map(lambda value: mapping.get(value, value))
    return pd.to_numeric(coerced, errors="coerce").fillna(0).astype(int)


def load_matches(data_dir: str | Path | None = None) -> pd.DataFrame:
    path = get_data_dir(data_dir) / MATCHES_FILENAME
    df = pd.read_csv(path)
    validate_columns(df, REQUIRED_MATCH_COLUMNS, str(path))

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["neutral"] = coerce_neutral_column(df["neutral"])

    for column in ["home_team", "away_team"]:
        df[column] = df[column].astype(str).str.strip().apply(normalize_team_name)

    return df.sort_values("date").reset_index(drop=True)


def load_group_matches(data_dir: str | Path | None = None) -> pd.DataFrame:
    path = get_data_dir(data_dir) / GROUP_MATCHES_FILENAME
    group_matches = pd.read_csv(path, encoding="utf-8-sig")
    group_matches.columns = (
        group_matches.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    )
    validate_columns(group_matches, REQUIRED_GROUP_COLUMNS, str(path))

    group_matches = group_matches[REQUIRED_GROUP_COLUMNS].copy()
    group_matches["group"] = group_matches["group"].astype(str).str.strip()
    group_matches["home_team"] = (
        group_matches["home_team"].astype(str).str.strip().apply(normalize_team_name)
    )
    group_matches["away_team"] = (
        group_matches["away_team"].astype(str).str.strip().apply(normalize_team_name)
    )

    return group_matches


def build_latest_team_data(matches: pd.DataFrame) -> pd.DataFrame:
    home_team_data = matches[
        ["date", "home_team", "home_fifa_rank", "home_fifa_points"]
    ].rename(
        columns={
            "home_team": "team",
            "home_fifa_rank": "fifa_rank",
            "home_fifa_points": "fifa_points",
        }
    )

    away_team_data = matches[
        ["date", "away_team", "away_fifa_rank", "away_fifa_points"]
    ].rename(
        columns={
            "away_team": "team",
            "away_fifa_rank": "fifa_rank",
            "away_fifa_points": "fifa_points",
        }
    )

    team_data = pd.concat([home_team_data, away_team_data], ignore_index=True)

    return (
        team_data.dropna(subset=["team", "fifa_rank", "fifa_points"])
        .sort_values("date")
        .groupby("team")
        .tail(1)
        .set_index("team")
        .sort_index()
    )


def split_train_test(
    matches: pd.DataFrame,
    cutoff_date: str = "2024-01-01",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    matches = matches.sort_values("date").copy()
    train = matches[matches["date"] < cutoff_date].copy()
    test = matches[matches["date"] >= cutoff_date].copy()

    if train.empty:
        raise ValueError("Training set is empty. Check cutoff_date or input data.")
    if test.empty:
        raise ValueError("Test set is empty. Check cutoff_date or input data.")

    return train, test


def prepare_xy(
    matches: pd.DataFrame,
    cutoff_date: str = "2024-01-01",
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    train, test = split_train_test(matches, cutoff_date=cutoff_date)
    return (
        train[FEATURES].copy(),
        train[TARGET].copy(),
        test[FEATURES].copy(),
        test[TARGET].copy(),
        train,
        test,
    )


def create_match_features(
    latest_team_data: pd.DataFrame,
    home_team: str,
    away_team: str,
    tournament: str = "FIFA World Cup",
    neutral: int = 1,
) -> pd.DataFrame:
    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)

    missing = [
        team
        for team in [home_team, away_team]
        if team not in latest_team_data.index
    ]
    if missing:
        raise ValueError(f"Missing ranking data for teams: {missing}")

    home_rank = latest_team_data.loc[home_team, "fifa_rank"]
    away_rank = latest_team_data.loc[away_team, "fifa_rank"]
    home_points = latest_team_data.loc[home_team, "fifa_points"]
    away_points = latest_team_data.loc[away_team, "fifa_points"]

    return pd.DataFrame(
        [
            {
                "home_fifa_rank": home_rank,
                "away_fifa_rank": away_rank,
                "home_fifa_points": home_points,
                "away_fifa_points": away_points,
                "fifa_rank_diff": home_rank - away_rank,
                "fifa_points_diff": home_points - away_points,
                "neutral": int(neutral),
                "tournament": tournament,
            }
        ]
    )


def missing_teams(teams: Iterable[str], latest_team_data: pd.DataFrame) -> list[str]:
    normalized_teams = [normalize_team_name(team) for team in teams]
    return sorted({team for team in normalized_teams if team not in latest_team_data.index})
