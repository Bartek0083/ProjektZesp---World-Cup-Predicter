"""Agregacja statystyk z timeline meczu."""

from __future__ import annotations

from typing import Any


def aggregate_timeline_stats(
    events: list[dict[str, Any]],
    home_team: str,
    away_team: str,
) -> dict[str, Any]:
    goals_home = goals_away = 0
    yellow_home = yellow_away = 0
    red_home = red_away = 0
    subs_home = subs_away = 0
    goal_minutes: list[dict[str, Any]] = []

    for event in events:
        etype = event.get("event_type") or ""
        team = event.get("team") or ""
        minute = event.get("minute", 0)
        is_home = team == home_team or event.get("side") == "home"

        if etype == "goal":
            if is_home:
                goals_home += 1
            else:
                goals_away += 1
            goal_minutes.append({"minute": minute, "team": team, "side": "home" if is_home else "away"})
        elif etype == "card":
            card = (event.get("extra") or {}).get("card_type", "yellow")
            if card == "red":
                if is_home:
                    red_home += 1
                else:
                    red_away += 1
            else:
                if is_home:
                    yellow_home += 1
                else:
                    yellow_away += 1
        elif etype == "substitution":
            if is_home:
                subs_home += 1
            else:
                subs_away += 1

    total_events = len(events)
    possession_home = 50
    if goals_home + goals_away > 0:
        possession_home = round(45 + (goals_home - goals_away) * 8 + min(goals_home, 3) * 2)
        possession_home = max(35, min(65, possession_home))

    return {
        "goals": {"home": goals_home, "away": goals_away},
        "cards": {
            "yellow": {"home": yellow_home, "away": yellow_away},
            "red": {"home": red_home, "away": red_away},
        },
        "substitutions": {"home": subs_home, "away": subs_away},
        "goal_minutes": goal_minutes,
        "possession_estimate": {"home": possession_home, "away": 100 - possession_home},
        "total_events": total_events,
    }
