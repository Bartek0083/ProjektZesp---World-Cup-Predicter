from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from data import DATA_DIR_ENV, load_group_matches
from match_engine import MatchMode, TournamentSettings, simulate_match as simulate_live_match
from model import evaluate_model, load_or_train_model, predict_match_proba
from simulator import (
    simulate_group_stage_many_times,
    simulate_world_cup_from_r32_pairings_many_times,
    simulate_world_cup_many_times_official_bracket,
)


MODEL_PATH_ENV = "WORLD_CUP_MODEL_PATH"
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "world_cup_model.joblib"
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = FastAPI(title="World Cup Predictor API", version="1.0.0")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    tournament: str = "FIFA World Cup"
    neutral: int = Field(default=1, ge=0, le=1)


class MatchSimulationRequest(BaseModel):
    home_team: str
    away_team: str
    mode: str = "friendly"
    neutral_venue: bool = True
    extra_time: bool = True
    golden_goal: bool = False
    penalties_after_90: bool = False
    seed: int | None = None


class GroupMatchRequest(BaseModel):
    group: str
    home_team: str
    away_team: str


class R32PairingRequest(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    home_slot: str | None = None
    away_slot: str | None = None


class GroupStageSimulationRequest(BaseModel):
    matches: list[GroupMatchRequest] | None = None
    n_simulations: int = Field(default=1_000, ge=1, le=20_000)
    include_simulations: bool = False


class WorldCupSimulationRequest(BaseModel):
    matches: list[GroupMatchRequest] | None = None
    r32_pairings: list[R32PairingRequest] | None = None
    n_simulations: int = Field(default=100, ge=1, le=5_000)
    include_knockout_results: bool = False


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.where(pd.notna(df), None).to_dict(orient="records")


def normalize_team_name(team: str) -> str:
    return " ".join(str(team or "").split()).casefold()


def ensure_distinct_teams(
    home_team: str,
    away_team: str,
    context: str = "Mecz",
    message: str | None = None,
) -> None:
    if normalize_team_name(home_team) and normalize_team_name(home_team) == normalize_team_name(away_team):
        raise ValueError(message or f"{context}: ta sama druzyna nie moze grac przeciwko sobie.")


def validate_group_match_requests(matches: list[GroupMatchRequest] | None) -> None:
    if matches is None:
        return

    team_groups: dict[str, tuple[str, str]] = {}
    for match in matches:
        ensure_distinct_teams(
            match.home_team,
            match.away_team,
            context=f"Grupa {match.group}",
        )

        for team in [match.home_team, match.away_team]:
            team_key = normalize_team_name(team)
            if not team_key:
                continue

            previous = team_groups.get(team_key)
            if previous is not None and previous[1] != match.group:
                raise ValueError(
                    f"{previous[0]} jest juz w grupie {previous[1]}. "
                    "Jedna druzyna moze byc tylko w jednej grupie."
                )

            team_groups[team_key] = (team, match.group)


def validate_r32_pairing_requests(pairings: list[R32PairingRequest]) -> None:
    for pairing in pairings:
        ensure_distinct_teams(
            pairing.home_team,
            pairing.away_team,
            context=f"Mecz {pairing.match_id}",
        )


def get_model_path() -> Path:
    return Path(os.getenv(MODEL_PATH_ENV, DEFAULT_MODEL_PATH)).expanduser().resolve()


def get_data_dir() -> str | None:
    return os.getenv(DATA_DIR_ENV)


@lru_cache(maxsize=1)
def get_trained_model():
    return load_or_train_model(
        model_path=get_model_path(),
        data_dir=get_data_dir(),
    )


def request_matches_to_df(matches: list[GroupMatchRequest] | None) -> pd.DataFrame:
    if matches is None:
        return load_group_matches(data_dir=get_data_dir())
    validate_group_match_requests(matches)
    return pd.DataFrame([model_to_dict(match) for match in matches])


def request_pairings_to_records(pairings: list[R32PairingRequest]) -> list[dict[str, Any]]:
    validate_r32_pairing_requests(pairings)
    return [model_to_dict(pairing) for pairing in pairings]


def build_simulation_team_ratings(latest_team_data: pd.DataFrame) -> dict[str, dict[str, float]]:
    ratings: dict[str, dict[str, float]] = {}
    for team, row in latest_team_data.iterrows():
        fifa_rank = float(row["fifa_rank"])
        fifa_points = float(row["fifa_points"])
        point_quality = max(0.0, min(1.0, (fifa_points - 850.0) / 1_050.0))
        rank_quality = max(0.0, min(1.0, (211.0 - fifa_rank) / 210.0))
        quality = (point_quality * 0.68) + (rank_quality * 0.32)
        ratings[str(team)] = {
            "fifa_rank": fifa_rank,
            "fifa_points": fifa_points,
            "attack": 50.0 + quality * 44.0,
            "defense": 50.0 + quality * 44.0,
        }
    return ratings


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    index_path = FRONTEND_DIR / "index.html"
    return index_path.read_text(encoding="utf-8")


@app.get("/teams")
def teams() -> dict[str, list[str]]:
    trained_model = get_trained_model()
    return {"teams": sorted(trained_model.latest_team_data.index.tolist())}


@app.get("/group-matches")
def group_matches() -> dict[str, Any]:
    return {"matches": records(load_group_matches(data_dir=get_data_dir()))}


@app.get("/evaluation")
def evaluation() -> dict[str, Any]:
    try:
        trained_model = get_trained_model()
        return evaluate_model(trained_model, data_dir=get_data_dir())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict-match")
def predict_match(request: MatchRequest) -> dict[str, Any]:
    try:
        ensure_distinct_teams(
            request.home_team,
            request.away_team,
            message="Nie mozna przeprowadzic predykcji meczu dla tych samych druzyn.",
        )
        trained_model = get_trained_model()
        return predict_match_proba(
            trained_model=trained_model,
            home_team=request.home_team,
            away_team=request.away_team,
            tournament=request.tournament,
            neutral=request.neutral,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/simulate-match")
def simulate_match_endpoint(request: MatchSimulationRequest) -> dict[str, Any]:
    try:
        ensure_distinct_teams(
            request.home_team,
            request.away_team,
            message="Nie mozna przeprowadzic symulacji meczu dla tych samych druzyn.",
        )
        trained_model = get_trained_model()
        mode = MatchMode(request.mode)
        settings = TournamentSettings(
            extra_time=request.extra_time,
            golden_goal=request.golden_goal,
            penalties_after_90=request.penalties_after_90,
        )
        result = simulate_live_match(
            home_team=request.home_team,
            away_team=request.away_team,
            mode=mode,
            settings=settings,
            neutral_venue=request.neutral_venue,
            seed=request.seed,
            team_ratings=build_simulation_team_ratings(trained_model.latest_team_data),
        )
        return result.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/simulate-group-stage")
def simulate_group_stage(request: GroupStageSimulationRequest) -> dict[str, Any]:
    try:
        validate_group_match_requests(request.matches)
        trained_model = get_trained_model()
        group_matches = request_matches_to_df(request.matches)
        summary, simulations, group_matches_with_proba = simulate_group_stage_many_times(
            trained_model=trained_model,
            group_matches=group_matches,
            n_simulations=request.n_simulations,
            include_simulations=request.include_simulations,
        )
        return {
            "n_simulations": request.n_simulations,
            "summary": records(summary),
            "match_probabilities": records(group_matches_with_proba),
            **({"simulations": records(simulations)} if request.include_simulations else {}),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/simulate-world-cup")
def simulate_world_cup(request: WorldCupSimulationRequest) -> dict[str, Any]:
    try:
        validate_group_match_requests(request.matches)
        if request.r32_pairings is not None:
            validate_r32_pairing_requests(request.r32_pairings)

        trained_model = get_trained_model()
        if request.r32_pairings is not None:
            summary, knockout_results = simulate_world_cup_from_r32_pairings_many_times(
                trained_model=trained_model,
                r32_pairings=request_pairings_to_records(request.r32_pairings),
                n_simulations=request.n_simulations,
                include_knockout_results=request.include_knockout_results,
                collect_all_knockout_results=False,
            )
            response: dict[str, Any] = {
                "n_simulations": request.n_simulations,
                "summary": records(summary),
                "match_probabilities": [],
            }
            if request.include_knockout_results:
                response["knockout_results"] = records(knockout_results)
            return response

        group_matches = request_matches_to_df(request.matches)
        summary, knockout_results, group_matches_with_proba = (
            simulate_world_cup_many_times_official_bracket(
                trained_model=trained_model,
                group_matches=group_matches,
                n_simulations=request.n_simulations,
                include_knockout_results=request.include_knockout_results,
                collect_all_knockout_results=False,
            )
        )
        response: dict[str, Any] = {
            "n_simulations": request.n_simulations,
            "summary": records(summary),
            "match_probabilities": records(group_matches_with_proba),
        }
        if request.include_knockout_results:
            response["knockout_results"] = records(knockout_results)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
