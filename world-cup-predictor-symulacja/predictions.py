"""Predykcja wyniku i podgląd meczu przed symulacją."""

from __future__ import annotations

import math
from typing import Any

from teams_data import get_team_rating


def _expected_goals(attack: float, defense: float) -> float:
    return max(0.35, (attack / 88.0) * ((100.0 - defense) / 100.0) * 1.55)


def _poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def _match_outcome_probs(home_xg: float, away_xg: float, max_goals: int = 8) -> dict[str, float]:
    home_win = draw = away_win = 0.0
    for h in range(max_goals + 1):
        ph = _poisson_pmf(h, home_xg)
        for a in range(max_goals + 1):
            pa = _poisson_pmf(a, away_xg)
            p = ph * pa
            if h > a:
                home_win += p
            elif h < a:
                away_win += p
            else:
                draw += p
    total = home_win + draw + away_win or 1.0
    return {
        "home_win": round(home_win / total * 100, 1),
        "draw": round(draw / total * 100, 1),
        "away_win": round(away_win / total * 100, 1),
    }


def compute_match_preview(
    home_team: str,
    away_team: str,
    *,
    neutral_venue: bool = True,
) -> dict[str, Any]:
    """Podgląd siły drużyn i szacunkowe prawdopodobieństwa wyniku."""
    home = get_team_rating(home_team)
    away = get_team_rating(away_team)

    home_attack = home["attack"] + (0 if neutral_venue else 3)
    home_defense = home["defense"] + (0 if neutral_venue else 2)
    away_attack = away["attack"]
    away_defense = away["defense"]

    home_xg = round(_expected_goals(home_attack, away_defense), 2)
    away_xg = round(_expected_goals(away_attack, home_defense), 2)
    probs = _match_outcome_probs(home_xg, away_xg)

    strength_home = round((home_attack + home_defense) / 2, 1)
    strength_away = round((away_attack + away_defense) / 2, 1)

    favorite = home_team
    if strength_away > strength_home:
        favorite = away_team
    elif abs(strength_home - strength_away) < 1.5:
        favorite = None

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home": {
            "attack": home_attack,
            "defense": home_defense,
            "strength": strength_home,
            "expected_goals": home_xg,
        },
        "away": {
            "attack": away_attack,
            "defense": away_defense,
            "strength": strength_away,
            "expected_goals": away_xg,
        },
        "probabilities": probs,
        "expected_score": f"{home_xg:.1f} : {away_xg:.1f}",
        "favorite": favorite,
        "neutral_venue": neutral_venue,
    }


def compare_real_vs_simulation(
    real_home: int,
    real_away: int,
    sim_home: int,
    sim_away: int,
) -> dict[str, Any]:
    """Porównanie wyniku rzeczywistego z symulacją."""
    real_diff = real_home - real_away
    sim_diff = sim_home - sim_away
    outcome_match = (
        (real_diff > 0 and sim_diff > 0)
        or (real_diff < 0 and sim_diff < 0)
        or (real_diff == 0 and sim_diff == 0)
    )
    return {
        "real_score": f"{real_home}:{real_away}",
        "simulated_score": f"{sim_home}:{sim_away}",
        "exact_score_match": real_home == sim_home and real_away == sim_away,
        "outcome_match": outcome_match,
        "goal_diff_error": abs(real_diff - sim_diff),
        "total_goals_real": real_home + real_away,
        "total_goals_sim": sim_home + sim_away,
    }
