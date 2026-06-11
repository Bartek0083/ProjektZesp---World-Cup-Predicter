"""API FastAPI — symulacja meczu z animowanym przebiegiem."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from match_engine import MatchMode, TournamentSettings, simulate_match
from sportsdb_client import (
    get_match_details,
    get_match_timeline,
    get_matches_today,
    get_teams,
    get_upcoming_matches,
    refresh_matches_cache,
    refresh_teams_cache,
    resolve_simulation_team_name,
)
from teams_data import list_teams


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = FastAPI(title="World Cup — Symulacja Meczu", version="1.0.0")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class SimulateRequest(BaseModel):
    home_team: str
    away_team: str
    mode: str = Field(default="friendly", pattern="^(friendly|tournament)$")
    seed: int | None = None
    neutral_venue: bool = True
    extra_time: bool = True
    golden_goal: bool = False
    penalties_after_90: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/teams")
def teams() -> dict:
    cached = get_teams()
    if cached:
        return {
            "teams": cached,
            "count": len(cached),
            "source": "cache",
        }
    # fallback — sama lista nazw z teams_data
    fallback = [{"name": name, "badge": None, "country": name, "rating": None}
                for name in list_teams()]
    return {"teams": fallback, "count": len(fallback), "source": "fallback"}


@app.post("/teams/refresh")
def teams_refresh() -> dict:
    """Odświeża cache drużyn z TheSportsDB (proxy backend — klucz tylko po stronie serwera)."""
    try:
        teams, source = refresh_teams_cache()
        return {
            "teams": teams,
            "count": len(teams),
            "source": source,
            "refreshed": True,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Błąd odświeżania cache: {exc}") from exc


@app.get("/matches")
def matches_list(date: str | None = Query(default=None, description="Data YYYY-MM-DD")) -> dict:
    """Lista meczów piłkarskich na dziś lub podaną datę (TheSportsDB eventsday)."""
    items, source, resolved_date = get_matches_today(date_str=date)
    return {
        "matches": items,
        "count": len(items),
        "date": resolved_date,
        "source": source,
        "free_tier_note": (
            "Free tier: max 3 mecze/dzień przez eventsday; brak livescore v2 (premium). "
            "Pokazujemy mecze na dziś i nadchodzące z eventsnextleague."
        ),
    }


@app.get("/matches/upcoming")
def matches_upcoming(
    league_id: str | None = Query(default=None, description="Opcjonalne idLeague"),
) -> dict:
    """Najbliższe mecze z mundialu i popularnych lig."""
    items, source = get_upcoming_matches(league_id=league_id)
    return {
        "matches": items,
        "count": len(items),
        "source": source,
        "league_id": league_id,
        "free_tier_note": (
            "Free tier: eventsnextleague zwraca 1 najbliższy mecz na ligę. "
            "Pełny livescore na żywo wymaga konta premium."
        ),
    }


@app.get("/matches/{event_id}")
def match_details(event_id: str, timeline: bool = Query(default=False)) -> dict:
    """Szczegóły meczu; ?timeline=1 dołącza przebieg."""
    match = get_match_details(event_id, include_timeline=timeline)
    if not match:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono meczu: {event_id}")
    sim_home = resolve_simulation_team_name(match["home_team"])
    sim_away = resolve_simulation_team_name(match["away_team"])
    return {
        "match": match,
        "simulation_teams": {
            "home": sim_home,
            "away": sim_away,
            "can_simulate": bool(sim_home and sim_away),
        },
    }


@app.get("/matches/{event_id}/timeline")
def match_timeline(event_id: str) -> dict:
    """Prawdziwy timeline meczu (bramki, kartki, zmiany)."""
    match = get_match_details(event_id, include_timeline=False)
    if not match:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono meczu: {event_id}")
    events, timeline_source = get_match_timeline(event_id, match=match)
    return {
        "event_id": event_id,
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "home_score": match.get("home_score"),
        "away_score": match.get("away_score"),
        "status": match.get("status"),
        "is_finished": match.get("is_finished", False),
        "is_upcoming": match.get("is_upcoming", False),
        "is_live": match.get("is_live", False),
        "events": events,
        "timeline_source": timeline_source,
        "source": match.get("source", "thesportsdb"),
    }


@app.post("/matches/refresh")
def matches_refresh() -> dict:
    """Odświeża cache meczów z TheSportsDB."""
    try:
        cache = refresh_matches_cache()
        return {
            "refreshed": True,
            "updated_at": cache.get("updated_at"),
            "today": cache.get("today"),
            "upcoming": cache.get("upcoming"),
            "note": cache.get("note"),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Błąd odświeżania meczów: {exc}") from exc


@app.post("/simulate-match")
def simulate_match_endpoint(request: SimulateRequest) -> dict:
    try:
        settings = TournamentSettings(
            extra_time=request.extra_time,
            golden_goal=request.golden_goal,
            penalties_after_90=request.penalties_after_90,
        )
        result = simulate_match(
            home_team=request.home_team.strip(),
            away_team=request.away_team.strip(),
            mode=MatchMode(request.mode),
            settings=settings if request.mode == "tournament" else None,
            seed=request.seed,
            neutral_venue=request.neutral_venue,
        )
        return result.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
