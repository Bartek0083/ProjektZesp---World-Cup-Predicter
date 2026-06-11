"""Oceny siły drużyn używane w symulacji (skala 0–100, uproszczone rankingi FIFA)."""

from __future__ import annotations

TEAM_RATINGS: dict[str, dict[str, float]] = {
    "Argentina": {"attack": 88, "defense": 85, "fifa_points": 1855},
    "France": {"attack": 87, "defense": 86, "fifa_points": 1840},
    "Brazil": {"attack": 86, "defense": 82, "fifa_points": 1830},
    "England": {"attack": 84, "defense": 83, "fifa_points": 1800},
    "Spain": {"attack": 85, "defense": 84, "fifa_points": 1795},
    "Germany": {"attack": 83, "defense": 84, "fifa_points": 1780},
    "Portugal": {"attack": 84, "defense": 80, "fifa_points": 1770},
    "Netherlands": {"attack": 83, "defense": 81, "fifa_points": 1760},
    "Belgium": {"attack": 82, "defense": 79, "fifa_points": 1750},
    "Croatia": {"attack": 80, "defense": 82, "fifa_points": 1740},
    "Italy": {"attack": 81, "defense": 85, "fifa_points": 1735},
    "Uruguay": {"attack": 79, "defense": 83, "fifa_points": 1720},
    "Colombia": {"attack": 80, "defense": 78, "fifa_points": 1710},
    "Mexico": {"attack": 76, "defense": 75, "fifa_points": 1680},
    "United States": {"attack": 77, "defense": 76, "fifa_points": 1675},
    "Japan": {"attack": 75, "defense": 78, "fifa_points": 1660},
    "Morocco": {"attack": 76, "defense": 80, "fifa_points": 1655},
    "Switzerland": {"attack": 74, "defense": 79, "fifa_points": 1640},
    "Poland": {"attack": 72, "defense": 77, "fifa_points": 1620},
    "Senegal": {"attack": 74, "defense": 76, "fifa_points": 1610},
    "South Korea": {"attack": 73, "defense": 77, "fifa_points": 1600},
    "Australia": {"attack": 71, "defense": 74, "fifa_points": 1580},
    "Ecuador": {"attack": 72, "defense": 73, "fifa_points": 1570},
    "Denmark": {"attack": 73, "defense": 75, "fifa_points": 1565},
    "Serbia": {"attack": 72, "defense": 74, "fifa_points": 1555},
    "Wales": {"attack": 70, "defense": 73, "fifa_points": 1540},
    "Iran": {"attack": 71, "defense": 76, "fifa_points": 1535},
    "Costa Rica": {"attack": 68, "defense": 72, "fifa_points": 1520},
    "Saudi Arabia": {"attack": 69, "defense": 70, "fifa_points": 1510},
    "Cameroon": {"attack": 70, "defense": 71, "fifa_points": 1505},
    "Canada": {"attack": 69, "defense": 70, "fifa_points": 1495},
    "Ghana": {"attack": 70, "defense": 69, "fifa_points": 1485},
    "Tunisia": {"attack": 68, "defense": 72, "fifa_points": 1475},
    "Qatar": {"attack": 65, "defense": 68, "fifa_points": 1450},
    "South Africa": {"attack": 68, "defense": 72, "fifa_points": 1465},
}


def list_teams() -> list[str]:
    return sorted(TEAM_RATINGS.keys())


def get_team_rating(team: str) -> dict[str, float]:
    try:
        from sportsdb_client import resolve_rating

        cached = resolve_rating(team)
        if cached:
            return cached
    except Exception:
        pass

    if team in TEAM_RATINGS:
        return TEAM_RATINGS[team]

    raise ValueError(f"Nieznana drużyna: {team}. Dostępne: {', '.join(list_teams()[:5])}...")
