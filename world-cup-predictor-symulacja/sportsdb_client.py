"""Klient TheSportsDB v1 z lokalnym cache JSON drużyn."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from teams_data import TEAM_RATINGS

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("THESPORTSDB_API_KEY", "123")
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/"
DATA_DIR = Path(__file__).resolve().parent / "data"
CACHE_PATH = DATA_DIR / "teams_cache.json"
MATCHES_CACHE_PATH = DATA_DIR / "matches_cache.json"
MATCHES_SEED_PATH = DATA_DIR / "matches_seed.json"
MIN_TEAMS = 10
REQUEST_DELAY_SEC = 0.6  # free tier — unikaj zbyt częstych zapytań
MATCHES_CACHE_TTL_SEC = 20 * 60  # 20 minut

# Popularne ligi piłkarskie (free tier: eventsnextleague zwraca 1 mecz na ligę)
POPULAR_LEAGUE_IDS = {
    "4429": "FIFA World Cup",
    "4480": "UEFA Champions League",
    "4328": "English Premier League",
    "4335": "Spanish La Liga",
    "4331": "German Bundesliga",
    "4332": "Italian Serie A",
}

TEAM_NAME_ALIASES: dict[str, str] = {
    "usa": "United States",
    "u.s.a.": "United States",
    "korea republic": "South Korea",
    "republic of korea": "South Korea",
    "korea": "South Korea",
}

# Kraje reprezentacji często obecnych na mundialu (list teams po kraju działa na free tier)
WORLD_CUP_COUNTRIES = [
    "Argentina", "Australia", "Belgium", "Brazil", "Cameroon", "Canada",
    "Costa Rica", "Croatia", "Denmark", "Ecuador", "England", "France",
    "Germany", "Ghana", "Iran", "Japan", "Mexico", "Morocco", "Netherlands",
    "Poland", "Portugal", "Qatar", "Saudi Arabia", "Senegal", "Serbia",
    "South Korea", "Spain", "Switzerland", "Tunisia", "United States",
    "Uruguay", "Wales", "Italy", "Colombia",
]

def _rating_from_rank(rank: int, total: int) -> dict[str, float]:
    """Prosty rating z pozycji w rankingu (1 = najsilniejsza)."""
    if total <= 1:
        strength = 75.0
    else:
        strength = 88.0 - (rank - 1) * (23.0 / max(total - 1, 1))
    strength = round(max(60.0, min(92.0, strength)), 1)
    return {
        "rating": strength,
        "attack": strength,
        "defense": round(strength - 2.0, 1),
        "fifa_points": round(strength * 21.0),
    }


def _team_from_seed(name: str, rank: int, total: int) -> dict[str, Any]:
    base = TEAM_RATINGS.get(name, _rating_from_rank(rank, total))
    return {
        "id": f"seed-{name.lower().replace(' ', '-')}",
        "name": name,
        "country": name,
        "badge": None,
        "rating": base.get("attack", 75.0),
        "attack": base["attack"],
        "defense": base["defense"],
        "fifa_points": base.get("fifa_points", 1500),
        "source": "seed",
    }


def _seed_teams() -> list[dict[str, Any]]:
    names = sorted(TEAM_RATINGS.keys())
    total = len(names)
    return [_team_from_seed(name, idx + 1, total) for idx, name in enumerate(names)]


def _national_team_entry(raw: dict[str, Any], country: str) -> dict[str, Any] | None:
    """Buduje wpis reprezentacji — nazwa kanoniczna z teams_data jeśli dostępna."""
    name = country if country in TEAM_RATINGS else (raw.get("strTeam") or country).strip()
    if not name:
        return None

    rank_names = sorted(TEAM_RATINGS.keys())
    rank = rank_names.index(name) + 1 if name in rank_names else len(rank_names)
    ratings = TEAM_RATINGS.get(name) or _rating_from_rank(rank, len(rank_names))
    badge = raw.get("strBadge") or raw.get("strTeamBadge")

    return {
        "id": str(raw.get("idTeam") or name),
        "name": name,
        "country": country,
        "badge": badge if badge else None,
        "rating": ratings["attack"],
        "attack": ratings["attack"],
        "defense": ratings["defense"],
        "fifa_points": ratings.get("fifa_points", ratings["attack"] * 21),
        "source": "thesportsdb",
    }


def _api_get(endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any] | None:
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=12)
            if response.status_code == 429:
                time.sleep(2.0 * (attempt + 1))
                continue
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt < 2:
                time.sleep(1.5)
                continue
            logger.warning("TheSportsDB %s: %s", endpoint, exc)
            return None
    return None


def _pick_national_team(teams: list[dict[str, Any]], country: str) -> dict[str, Any] | None:
    country_l = country.lower()
    for team in teams:
        sport = (team.get("strSport") or "").lower()
        if sport and sport != "soccer":
            continue
        name = (team.get("strTeam") or "").lower()
        team_country = (team.get("strCountry") or "").lower()
        if name == country_l or team_country == country_l:
            return team
    for team in teams:
        name = (team.get("strTeam") or "").lower()
        if country_l in name and "u21" not in name and "u23" not in name:
            return team
    return teams[0] if teams else None


def _fetch_from_api() -> list[dict[str, Any]]:
    """Pobiera reprezentacje po kraju (free tier — bez searchteams po nazwie klubu)."""
    collected: dict[str, dict[str, Any]] = {}

    for country in WORLD_CUP_COUNTRIES:
        payload = _api_get("search_all_teams.php", {"s": "Soccer", "c": country})
        if not payload or not payload.get("teams"):
            time.sleep(REQUEST_DELAY_SEC)
            continue
        picked = _pick_national_team(payload["teams"], country)
        if picked:
            entry = _national_team_entry(picked, country)
            if entry:
                collected[entry["name"]] = entry
        time.sleep(REQUEST_DELAY_SEC)

    return sorted(collected.values(), key=lambda t: t["name"].lower())


def _merge_with_seed(api_teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Uzupełnia brakujące reprezentacje seedem; zachowuje badge z API."""
    by_name = {t["name"]: t for t in api_teams}
    for team in _seed_teams():
        existing = by_name.get(team["name"])
        if existing:
            if not existing.get("badge") and team.get("badge"):
                existing["badge"] = team["badge"]
        else:
            by_name[team["name"]] = team
    return sorted(by_name.values(), key=lambda t: t["name"].lower())


def _read_cache_file() -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Nie można odczytać cache: %s", exc)
        return None


def _write_cache(teams: list[dict[str, Any]], source: str) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "teams": teams,
    }
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def refresh_teams_cache() -> tuple[list[dict[str, Any]], str]:
    """Pobiera drużyny z API i zapisuje cache. Zwraca (teams, source)."""
    api_teams = _fetch_from_api()
    teams = _merge_with_seed(api_teams)
    if api_teams and len(api_teams) >= MIN_TEAMS:
        source = "thesportsdb"
    elif api_teams:
        source = "thesportsdb+seed"
    else:
        source = "seed"
    _write_cache(teams, source)
    return teams, source


def get_teams(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Zwraca listę drużyn z cache (lub odświeża z API)."""
    if force_refresh:
        teams, _ = refresh_teams_cache()
        return teams

    cached = _read_cache_file()
    if cached and cached.get("teams"):
        return cached["teams"]

    teams, _ = refresh_teams_cache()
    if teams:
        return teams

    seed = _seed_teams()
    _write_cache(seed, "seed")
    return seed


def get_team_by_name(name: str) -> dict[str, Any] | None:
    """Szuka drużyny po nazwie (dokładnie lub w cache)."""
    target = name.strip()
    for team in get_teams():
        if team["name"] == target:
            return team
    return None


def resolve_rating(team_name: str) -> dict[str, float] | None:
    """Rating do symulacji — z cache TheSportsDB lub None."""
    team = get_team_by_name(team_name)
    if not team:
        return None
    return {
        "attack": float(team["attack"]),
        "defense": float(team["defense"]),
        "fifa_points": float(team.get("fifa_points", team["rating"] * 21)),
    }


# --- Mecze z TheSportsDB ---


def _parse_score(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_finished_status(status: str) -> bool:
    s = (status or "").upper()
    return s in {"FT", "AET", "PEN", "AWD", "WO"}


def _is_live_status(status: str) -> bool:
    s = (status or "").upper()
    return s in {"1H", "2H", "HT", "ET", "BT", "P", "LIVE", "INT"}


def _is_upcoming_status(status: str) -> bool:
    s = (status or "").upper()
    return s in {"", "NS", "TBD", "SCHEDULED", "NOT STARTED"}


def _normalize_team_name(name: str) -> str:
    key = name.strip().lower()
    return TEAM_NAME_ALIASES.get(key, name.strip())


def resolve_simulation_team_name(api_name: str) -> str | None:
    """Mapuje nazwę z API na nazwę znaną symulatorowi."""
    canonical = _normalize_team_name(api_name)
    if get_team_by_name(canonical):
        return canonical
    if canonical in TEAM_RATINGS:
        return canonical
    canonical_l = canonical.lower()
    for team in get_teams():
        if team["name"].lower() == canonical_l:
            return team["name"]
        country = (team.get("country") or "").lower()
        if country and country == canonical_l:
            return team["name"]
    return None


def _event_to_match(raw: dict[str, Any], source: str = "thesportsdb") -> dict[str, Any]:
    status = (raw.get("strStatus") or "").strip()
    home_score = _parse_score(raw.get("intHomeScore"))
    away_score = _parse_score(raw.get("intAwayScore"))
    finished = _is_finished_status(status) or (
        home_score is not None and away_score is not None and not _is_live_status(status)
    )
    upcoming = _is_upcoming_status(status) and not finished

    return {
        "id": str(raw.get("idEvent") or ""),
        "home_team": _normalize_team_name(raw.get("strHomeTeam") or ""),
        "away_team": _normalize_team_name(raw.get("strAwayTeam") or ""),
        "home_badge": raw.get("strHomeTeamBadge") or None,
        "away_badge": raw.get("strAwayTeamBadge") or None,
        "date": raw.get("dateEvent") or raw.get("dateEventLocal") or "",
        "time": raw.get("strTime") or raw.get("strTimeLocal") or "",
        "league": raw.get("strLeague") or "",
        "league_id": str(raw.get("idLeague") or ""),
        "status": status or "NS",
        "home_score": home_score,
        "away_score": away_score,
        "is_finished": finished,
        "is_upcoming": upcoming,
        "is_live": _is_live_status(status),
        "venue": raw.get("strVenue") or "",
        "source": source,
    }


def _read_matches_seed() -> dict[str, Any]:
    if not MATCHES_SEED_PATH.exists():
        return {"matches_today": [], "upcoming": [], "details": {}, "timelines": {}}
    try:
        return json.loads(MATCHES_SEED_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Nie można odczytać seed meczów: %s", exc)
        return {"matches_today": [], "upcoming": [], "details": {}, "timelines": {}}


def _read_matches_cache() -> dict[str, Any] | None:
    if not MATCHES_CACHE_PATH.exists():
        return None
    try:
        return json.loads(MATCHES_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Nie można odczytać cache meczów: %s", exc)
        return None


def _write_matches_cache(payload: dict[str, Any]) -> None:
    MATCHES_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MATCHES_CACHE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _cache_is_fresh(cached: dict[str, Any] | None) -> bool:
    if not cached or not cached.get("updated_at"):
        return False
    try:
        updated = datetime.fromisoformat(cached["updated_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - updated.astimezone(timezone.utc)).total_seconds()
        return age < MATCHES_CACHE_TTL_SEC
    except (TypeError, ValueError):
        return False


def _dedupe_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for match in matches:
        mid = match.get("id") or f"{match.get('date')}-{match.get('home_team')}-{match.get('away_team')}"
        if mid in seen:
            continue
        seen.add(mid)
        result.append(match)
    return result


def _fetch_events_for_date(date_str: str) -> list[dict[str, Any]]:
    payload = _api_get("eventsday.php", {"d": date_str, "s": "Soccer"})
    if not payload or not payload.get("events"):
        return []
    return [_event_to_match(ev) for ev in payload["events"]]


def _fetch_upcoming_for_league(league_id: str) -> list[dict[str, Any]]:
    payload = _api_get("eventsnextleague.php", {"id": league_id})
    if not payload or not payload.get("events"):
        return []
    return [_event_to_match(ev) for ev in payload["events"]]


def _fetch_upcoming_from_api(league_id: str | None = None) -> list[dict[str, Any]]:
    leagues = [league_id] if league_id else list(POPULAR_LEAGUE_IDS.keys())
    collected: list[dict[str, Any]] = []
    for lid in leagues:
        if not lid:
            continue
        collected.extend(_fetch_upcoming_for_league(lid))
        time.sleep(REQUEST_DELAY_SEC)
    return _dedupe_matches(collected)


def refresh_matches_cache(date_str: str | None = None) -> dict[str, Any]:
    """Pobiera mecze z API i zapisuje cache. Zwraca pełny obiekt cache."""
    today = date_str or datetime.now().date().isoformat()
    today_matches = _fetch_events_for_date(today)
    today_source = "thesportsdb" if today_matches else "seed"

    upcoming = _fetch_upcoming_from_api()
    upcoming_source = "thesportsdb" if upcoming else "seed"

    seed = _read_matches_seed()
    if not today_matches:
        today_matches = [dict(m) for m in seed.get("matches_today", [])]
        today_source = "seed"
    if not upcoming:
        upcoming = [dict(m) for m in seed.get("upcoming", [])]
        upcoming_source = "seed"

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "today": {
            "date": today,
            "matches": today_matches,
            "source": today_source,
        },
        "upcoming": {
            "matches": upcoming,
            "source": upcoming_source,
        },
        "note": (
            "Free tier: brak livescore v2 — używamy eventsday/eventsnextleague. "
            "Pełny livescore wymaga premium."
        ),
    }
    _write_matches_cache(payload)
    return payload


def _ensure_matches_cache(force_refresh: bool = False) -> dict[str, Any]:
    if not force_refresh:
        cached = _read_matches_cache()
        if cached and _cache_is_fresh(cached):
            return cached
    return refresh_matches_cache()


def get_matches_today(
    date_str: str | None = None,
    force_refresh: bool = False,
) -> tuple[list[dict[str, Any]], str, str]:
    """Mecze piłkarskie na dany dzień (domyślnie dziś). Zwraca (matches, source, date)."""
    target = date_str or datetime.now().date().isoformat()
    today_iso = datetime.now().date().isoformat()

    if force_refresh or target != today_iso:
        if target == today_iso and force_refresh:
            cache = refresh_matches_cache(target)
        else:
            api_matches = _fetch_events_for_date(target)
            if api_matches:
                return api_matches, "thesportsdb", target
            seed = _read_matches_seed()
            fallback = [
                dict(m) for m in seed.get("matches_today", [])
                if m.get("date") == target
            ]
            if not fallback:
                fallback = [dict(m) for m in seed.get("matches_today", [])]
            return fallback, "seed", target

    cache = _ensure_matches_cache(force_refresh)
    section = cache.get("today", {})
    if section.get("date") == target:
        return section.get("matches", []), section.get("source", "cache"), target

    api_matches = _fetch_events_for_date(target)
    if api_matches:
        return api_matches, "thesportsdb", target

    seed = _read_matches_seed()
    fallback = [dict(m) for m in seed.get("matches_today", []) if m.get("date") == target]
    if not fallback:
        fallback = [dict(m) for m in seed.get("matches_today", [])]
    return fallback, "seed", target


def get_upcoming_matches(
    league_id: str | None = None,
    force_refresh: bool = False,
) -> tuple[list[dict[str, Any]], str]:
    """Najbliższe mecze z popularnych lig lub wskazanej ligi."""
    if force_refresh:
        cache = refresh_matches_cache()
    else:
        cache = _ensure_matches_cache(False)

    matches = cache.get("upcoming", {}).get("matches", [])
    source = cache.get("upcoming", {}).get("source", "cache")

    if league_id:
        matches = [m for m in matches if str(m.get("league_id")) == str(league_id)]

    if not matches and league_id:
        api_matches = _fetch_upcoming_from_api(league_id)
        if api_matches:
            return api_matches, "thesportsdb"

    if not matches:
        seed = _read_matches_seed()
        matches = [dict(m) for m in seed.get("upcoming", [])]
        if league_id:
            matches = [m for m in matches if str(m.get("league_id")) == str(league_id)]
        source = "seed"

    return matches, source


def _fetch_event_raw(event_id: str) -> dict[str, Any] | None:
    payload = _api_get("lookupevent.php", {"id": event_id})
    if not payload:
        return None
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        return None
    event = events[0]
    if not isinstance(event, dict):
        return None
    return event


def get_match_details(
    event_id: str,
    include_timeline: bool = False,
) -> dict[str, Any] | None:
    """Szczegóły meczu; opcjonalnie dołącza timeline."""
    raw = _fetch_event_raw(event_id)
    if raw:
        match = _event_to_match(raw)
        match["thumb"] = raw.get("strThumb")
        match["banner"] = raw.get("strBanner")
        match["round"] = raw.get("intRound")
        match["group"] = raw.get("strGroup")
        if include_timeline:
            events, timeline_source = get_match_timeline(event_id, match=match)
            match["timeline"] = events
            match["timeline_source"] = timeline_source
        return match

    seed = _read_matches_seed()
    details = seed.get("details", {})
    if event_id in details:
        match = dict(details[event_id])
        if include_timeline:
            events, timeline_source = get_match_timeline(event_id, match=match)
            match["timeline"] = events
            match["timeline_source"] = timeline_source
        return match

    return None


def _timeline_entry_to_event(
    entry: dict[str, Any],
    home_team: str,
    away_team: str,
    running_home: int,
    running_away: int,
) -> dict[str, Any] | None:
    kind = (entry.get("strTimeline") or "").lower()
    minute_raw = entry.get("intTime") or "0"
    try:
        minute = int(minute_raw)
    except (TypeError, ValueError):
        minute = 0

    team = entry.get("strTeam") or ""
    is_home = (entry.get("strHome") or "").lower() == "yes"
    if not team:
        team = home_team if is_home else away_team

    if kind == "goal":
        if is_home or team == home_team:
            running_home += 1
            scorer_team = home_team
        else:
            running_away += 1
            scorer_team = away_team
        player = entry.get("strPlayer") or ""
        assist = entry.get("strAssist") or ""
        desc = f"Gol — {scorer_team}"
        if player:
            desc += f" ({player}"
            if assist:
                desc += f", asysta: {assist}"
            desc += ")"
        desc += f" ({minute}')"
        return {
            "minute": minute,
            "event_type": "goal",
            "team": scorer_team,
            "description": desc,
            "home_score": running_home,
            "away_score": running_away,
            "phase": "regular",
        }

    if kind == "card":
        detail = entry.get("strTimelineDetail") or "Kartka"
        player = entry.get("strPlayer") or team
        return {
            "minute": minute,
            "event_type": "card",
            "team": team,
            "description": f"{detail} — {player} ({minute}')",
            "home_score": running_home,
            "away_score": running_away,
            "phase": "regular",
        }

    if kind in {"subst", "substitution"}:
        player = entry.get("strPlayer") or ""
        assist = entry.get("strAssist") or ""
        desc = f"Zmiana — {team}"
        if player:
            desc += f": {player}"
            if assist:
                desc += f" ↔ {assist}"
        desc += f" ({minute}')"
        return {
            "minute": minute,
            "event_type": "substitution",
            "team": team,
            "description": desc,
            "home_score": running_home,
            "away_score": running_away,
            "phase": "regular",
        }

    return None


def _goal_minutes_spread(count: int) -> list[int]:
    """Rozkłada bramki równomiernie w regulaminowym czasie (szacunek przy braku API)."""
    if count <= 0:
        return []
    if count == 1:
        return [45]
    return [int(10 + (75 * i / (count + 1))) for i in range(1, count + 1)]


def _build_timeline_from_score_fallback(
    home_team: str,
    away_team: str,
    home_score: int,
    away_score: int,
) -> list[dict[str, Any]]:
    """Minimalny przebieg z wyniku końcowego, gdy lookuptimeline jest pusty."""
    events: list[dict[str, Any]] = [
        {
            "minute": 0,
            "event_type": "kickoff",
            "team": None,
            "description": "Rozpoczęcie meczu",
            "home_score": 0,
            "away_score": 0,
            "phase": "regular",
        }
    ]
    running_home = 0
    running_away = 0

    goal_events: list[tuple[int, str]] = []
    for minute in _goal_minutes_spread(home_score):
        goal_events.append((minute, "home"))
    for minute in _goal_minutes_spread(away_score):
        goal_events.append((minute, "away"))
    goal_events.sort(key=lambda item: item[0])

    for minute, side in goal_events:
        if side == "home":
            running_home += 1
            team = home_team
        else:
            running_away += 1
            team = away_team
        events.append({
            "minute": minute,
            "event_type": "goal",
            "team": team,
            "description": (
                f"Gol — {team} ({minute}') "
                "(szacowany — brak szczegółów w TheSportsDB)"
            ),
            "home_score": running_home,
            "away_score": running_away,
            "phase": "regular",
        })

    events.append({
        "minute": 90,
        "event_type": "full_time",
        "team": None,
        "description": "Koniec meczu",
        "home_score": home_score,
        "away_score": away_score,
        "phase": "regular",
    })
    return events


def _build_timeline_from_api(
    entries: list[dict[str, Any]],
    home_team: str,
    away_team: str,
    home_score: int | None,
    away_score: int | None,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = [
        {
            "minute": 0,
            "event_type": "kickoff",
            "team": None,
            "description": "Rozpoczęcie meczu",
            "home_score": 0,
            "away_score": 0,
            "phase": "regular",
        }
    ]
    running_home = 0
    running_away = 0

    sorted_entries = sorted(
        entries,
        key=lambda e: int(e.get("intTime") or 0),
    )
    for entry in sorted_entries:
        converted = _timeline_entry_to_event(
            entry, home_team, away_team, running_home, running_away,
        )
        if not converted:
            continue
        if converted["event_type"] == "goal":
            running_home = converted["home_score"]
            running_away = converted["away_score"]
        events.append(converted)

    final_home = home_score if home_score is not None else running_home
    final_away = away_score if away_score is not None else running_away
    events.append({
        "minute": 90,
        "event_type": "full_time",
        "team": None,
        "description": "Koniec meczu",
        "home_score": final_home,
        "away_score": final_away,
        "phase": "regular",
    })
    return events


def _timeline_from_match_record(match: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Buduje minimalny timeline z wyniku meczu (lookupevent / cache)."""
    home_score = match.get("home_score")
    away_score = match.get("away_score")
    if home_score is None or away_score is None:
        return None
    if not (match.get("is_finished") or match.get("is_live")):
        return None
    return _build_timeline_from_score_fallback(
        match["home_team"],
        match["away_team"],
        int(home_score),
        int(away_score),
    )


def get_match_timeline(
    event_id: str,
    match: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Zdarzenia meczu z lookuptimeline lub fallbacku. Zwraca (events, source)."""
    details = match or get_match_details(event_id, include_timeline=False)

    payload = _api_get("lookuptimeline.php", {"id": event_id})
    timeline_raw = payload.get("timeline") if payload else None
    if isinstance(timeline_raw, list) and timeline_raw:
        home_team = details["home_team"] if details else ""
        away_team = details["away_team"] if details else ""
        home_score = details.get("home_score") if details else None
        away_score = details.get("away_score") if details else None
        return _build_timeline_from_api(
            timeline_raw, home_team, away_team, home_score, away_score,
        ), "api"

    seed = _read_matches_seed()
    timelines = seed.get("timelines", {})
    if event_id in timelines:
        return [dict(e) for e in timelines[event_id]], "seed"

    if details:
        fallback = _timeline_from_match_record(details)
        if fallback:
            return fallback, "score_fallback"

    seed_details = seed.get("details", {}).get(event_id)
    if seed_details:
        fallback = _timeline_from_match_record(seed_details)
        if fallback:
            return fallback, "score_fallback"

    return [], "empty"
