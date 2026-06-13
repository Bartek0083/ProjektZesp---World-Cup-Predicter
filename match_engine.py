"""Silnik symulacji meczu z przebiegiem minutowym, dogrywką i karnymi."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field
from enum import Enum
from math import exp
from typing import Any, Literal, Mapping

from teams_data import get_team_rating


class MatchMode(str, Enum):
    FRIENDLY = "friendly"
    TOURNAMENT = "tournament"


Phase = Literal["regular", "extra_first", "extra_second", "penalties"]


@dataclass
class TournamentSettings:
    """Ustawienia meczu pucharowego / turniejowego."""

    extra_time: bool = True
    golden_goal: bool = False
    penalties_after_90: bool = False


@dataclass
class MatchEvent:
    minute: int
    phase: Phase
    event_type: str
    team: str | None
    description: str
    home_score: int
    away_score: int
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PenaltyKick:
    team: str
    scored: bool
    kick_number: int
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MatchResult:
    home_team: str
    away_team: str
    mode: str
    settings: dict[str, Any]
    home_score_90: int
    away_score_90: int
    home_score_final: int
    away_score_final: int
    home_score_penalties: int | None
    away_score_penalties: int | None
    winner: str | None
    is_draw: bool
    decided_by: str
    events: list[MatchEvent]
    penalty_shootout: list[PenaltyKick]
    timeline_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "mode": self.mode,
            "settings": self.settings,
            "home_score_90": self.home_score_90,
            "away_score_90": self.away_score_90,
            "home_score_final": self.home_score_final,
            "away_score_final": self.away_score_final,
            "home_score_penalties": self.home_score_penalties,
            "away_score_penalties": self.away_score_penalties,
            "winner": self.winner,
            "is_draw": self.is_draw,
            "decided_by": self.decided_by,
            "events": [event.to_dict() for event in self.events],
            "penalty_shootout": [kick.to_dict() for kick in self.penalty_shootout],
            "timeline_summary": self.timeline_summary,
        }


TeamRating = Mapping[str, float | int]
TeamRatings = Mapping[str, TeamRating]


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _rating_quality(rating: TeamRating) -> float:
    components: list[float] = []

    fifa_points = rating.get("fifa_points")
    if fifa_points is not None:
        # FIFA points in this project usually sit roughly in the 850-1900 range.
        components.append(_clamp((float(fifa_points) - 850.0) / 1_050.0, 0.0, 1.0))

    fifa_rank = rating.get("fifa_rank")
    if fifa_rank is not None:
        components.append(_clamp((211.0 - float(fifa_rank)) / 210.0, 0.0, 1.0))

    attack = rating.get("attack")
    if attack is not None:
        components.append(_clamp((float(attack) - 45.0) / 50.0, 0.0, 1.0))

    defense = rating.get("defense")
    if defense is not None:
        components.append(_clamp((float(defense) - 45.0) / 50.0, 0.0, 1.0))

    if not components:
        return 0.5
    return sum(components) / len(components)


def _resolve_team_rating(team: str, team_ratings: TeamRatings | None = None) -> dict[str, float]:
    if team_ratings and team in team_ratings:
        return {key: float(value) for key, value in team_ratings[team].items()}
    return {key: float(value) for key, value in get_team_rating(team).items()}


def _goal_rate(attacker: TeamRating, defender: TeamRating, phase: Phase) -> float:
    attacker_quality = _rating_quality(attacker)
    defender_quality = _rating_quality(defender)
    quality_diff = attacker_quality - defender_quality

    expected_goals_90 = 1.10 * exp(1.55 * quality_diff)

    # Skrajne mismatch'e typu top 3 vs ranking 200+ realnie potrafia konczyc sie
    # bardzo wysoko, ale ten boost nie powinien dotykac wyrownanych meczow elit.
    mismatch = _clamp((quality_diff - 0.62) / 0.33, 0.0, 1.0)
    defender_weakness = _clamp((0.45 - defender_quality) / 0.45, 0.0, 1.0)
    expected_goals_90 += (mismatch ** 2) * defender_weakness * 3.0

    expected_goals_90 = _clamp(expected_goals_90, 0.08, 8.0)
    base = expected_goals_90 / 90.0
    if phase in ("extra_first", "extra_second"):
        return base * 0.75
    return base


def _sample_goal_minutes(
    rng: random.Random,
    count: int,
    minute_start: int,
    minute_end: int,
) -> list[int]:
    if count <= 0:
        return []
    weights = []
    minutes = list(range(minute_start, minute_end + 1))
    for minute in minutes:
        if minute <= 45:
            weight = 0.9
        elif minute <= 90:
            weight = 1.2
        else:
            weight = 1.0
        weights.append(weight)
    return sorted(rng.choices(minutes, weights=weights, k=count))


def _simulate_period_goals(
    rng: random.Random,
    home_team: str,
    away_team: str,
    home_rating: TeamRating,
    away_rating: TeamRating,
    phase: Phase,
    minute_start: int,
    minute_end: int,
) -> list[tuple[int, str]]:
    home_rate = _goal_rate(home_rating, away_rating, phase)
    away_rate = _goal_rate(away_rating, home_rating, phase)
    duration = minute_end - minute_start + 1

    home_goals = _poisson(rng, home_rate * duration)
    away_goals = _poisson(rng, away_rate * duration)
    home_minutes = _sample_goal_minutes(rng, home_goals, minute_start, minute_end)
    away_minutes = _sample_goal_minutes(rng, away_goals, minute_start, minute_end)

    goals: list[tuple[int, str]] = [(minute, home_team) for minute in home_minutes]
    goals.extend((minute, away_team) for minute in away_minutes)
    goals.sort(key=lambda item: item[0])
    return goals


def _goal_description(
    team: str,
    minute: int,
    phase: Phase,
    home_score: int,
    away_score: int,
    golden_goal: bool = False,
) -> str:
    if golden_goal:
        templates = [
            "ZŁOTA BRAMKA! {team} kończy mecz w {minute}'!",
            "{team} trafia w dogrywce - złoty gol w {minute}'!",
            "Złoty gol dla {team}! Decydujące uderzenie w {minute}'.",
        ]
    elif phase in ("extra_first", "extra_second"):
        templates = [
            "Gol dla {team} w dogrywce ({minute}').",
            "{team} wykorzystuje zmęczenie rywala i trafia w {minute}'.",
            "Bramka w dogrywce! {team} po dokładnym dośrodkowaniu ({minute}').",
            "{team} zdobywa gola po akcji z lewej strony w {minute}'.",
        ]
    else:
        templates = [
            "Gol dla {team}! Mocny strzał w {minute}'.",
            "{team} trafia po szybkiej akcji ({minute}').",
            "{team} wykorzystuje zamieszanie w polu karnym w {minute}'.",
            "Bramka dla {team}! Precyzyjne uderzenie przy słupku ({minute}').",
            "{team} finalizuje kontratak w {minute}'.",
            "Kapitalna akcja i gol dla {team} ({minute}').",
            "{team} zdobywa bramkę po dośrodkowaniu ({minute}').",
            "Strzał z dystansu i gol dla {team}! ({minute}')",
        ]

    key = f"{team}|{minute}|{phase}|{home_score}:{away_score}|{golden_goal}"
    return random.Random(key).choice(templates).format(team=team, minute=minute)


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    limit = min(12, max(6, int(lam * 3) + 4))
    count = 0
    product = 1.0
    threshold = pow(2.718281828, -lam)
    for _ in range(limit):
        product *= rng.random()
        if product < threshold:
            return count
        count += 1
    return count


def _penalty_success_chance(
    team: str,
    opponent: str,
    team_ratings: TeamRatings | None = None,
) -> float:
    rating = _resolve_team_rating(team, team_ratings)
    opp = _resolve_team_rating(opponent, team_ratings)
    base = 0.76 + (_rating_quality(rating) - _rating_quality(opp)) * 0.18
    return max(0.55, min(0.92, base))


def _simulate_penalty_shootout(
    rng: random.Random,
    home_team: str,
    away_team: str,
    team_ratings: TeamRatings | None = None,
) -> tuple[list[PenaltyKick], str, int, int]:
    kicks: list[PenaltyKick] = []
    home_scored = 0
    away_scored = 0
    kick_number = 0

    for round_index in range(5):
        for team, opponent, is_home in (
            (home_team, away_team, True),
            (away_team, home_team, False),
        ):
            kick_number += 1
            scored = rng.random() < _penalty_success_chance(team, opponent, team_ratings)
            if scored:
                if is_home:
                    home_scored += 1
                else:
                    away_scored += 1
            kicks.append(
                PenaltyKick(
                    team=team,
                    scored=scored,
                    kick_number=kick_number,
                    description="GOL z karnego!" if scored else "Pudło z karnego!",
                )
            )

        if home_scored != away_scored:
            remaining_home = 5 - (round_index + 1)
            remaining_away = 5 - (round_index + 1)
            if home_scored > away_scored + remaining_away:
                break
            if away_scored > home_scored + remaining_home:
                break

    while home_scored == away_scored:
        for team, opponent, is_home in (
            (home_team, away_team, True),
            (away_team, home_team, False),
        ):
            kick_number += 1
            scored = rng.random() < _penalty_success_chance(team, opponent, team_ratings)
            if scored:
                if is_home:
                    home_scored += 1
                else:
                    away_scored += 1
            kicks.append(
                PenaltyKick(
                    team=team,
                    scored=scored,
                    kick_number=kick_number,
                    description="GOL z karnego!" if scored else "Pudło z karnego!",
                )
            )
            if home_scored != away_scored:
                break

    winner = home_team if home_scored > away_scored else away_team
    return kicks, winner, home_scored, away_scored


def simulate_match(
    home_team: str,
    away_team: str,
    mode: MatchMode | str = MatchMode.FRIENDLY,
    settings: TournamentSettings | None = None,
    seed: int | None = None,
    neutral_venue: bool = True,
    team_ratings: TeamRatings | None = None,
) -> MatchResult:
    if isinstance(mode, str):
        mode = MatchMode(mode)

    tournament_settings = settings or TournamentSettings()
    rng = random.Random(seed)

    home_rating = _resolve_team_rating(home_team, team_ratings)
    away_rating = _resolve_team_rating(away_team, team_ratings)

    if not neutral_venue:
        home_rating = {
            **home_rating,
            "attack": float(home_rating.get("attack", 70.0)) + 2.2,
            "defense": float(home_rating.get("defense", 70.0)) + 1.4,
            "fifa_points": float(home_rating.get("fifa_points", 1_300.0)) + 18.0,
        }

    events: list[MatchEvent] = []
    penalty_shootout: list[PenaltyKick] = []
    home_score = 0
    away_score = 0

    events.append(
        MatchEvent(
            minute=0,
            phase="regular",
            event_type="kickoff",
            team=None,
            description=f"Rozpoczęcie meczu: {home_team} vs {away_team}",
            home_score=0,
            away_score=0,
        )
    )

    regular_goals = _simulate_period_goals(
        rng, home_team, away_team,
        home_rating, away_rating,
        "regular", 1, 90,
    )

    for minute, team in regular_goals:
        if team == home_team:
            home_score += 1
        else:
            away_score += 1
        events.append(
            MatchEvent(
                minute=minute,
                phase="regular",
                event_type="goal",
                team=team,
                description=_goal_description(team, minute, "regular", home_score, away_score),
                home_score=home_score,
                away_score=away_score,
            )
        )

    events.append(
        MatchEvent(
            minute=90,
            phase="regular",
            event_type="full_time",
            team=None,
            description=f"Koniec regulaminowego czasu: {home_score}:{away_score}",
            home_score=home_score,
            away_score=away_score,
        )
    )

    home_score_90 = home_score
    away_score_90 = away_score
    decided_by = "90_minutes"
    winner: str | None = None
    is_draw = home_score == away_score
    home_pen_score: int | None = None
    away_pen_score: int | None = None

    if mode == MatchMode.FRIENDLY:
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team
        else:
            winner = None
            is_draw = True
    elif home_score != away_score:
        winner = home_team if home_score > away_score else away_team
        is_draw = False
    elif tournament_settings.penalties_after_90:
        events.append(
            MatchEvent(
                minute=90,
                phase="penalties",
                event_type="phase_start",
                team=None,
                description="Remis po 90 minutach — od razu rzuty karne!",
                home_score=home_score,
                away_score=away_score,
            )
        )
        penalty_shootout, winner, home_pen_score, away_pen_score = _simulate_penalty_shootout(
            rng, home_team, away_team, team_ratings
        )
        for kick in penalty_shootout:
            events.append(
                MatchEvent(
                    minute=90,
                    phase="penalties",
                    event_type="penalty_goal" if kick.scored else "penalty_miss",
                    team=kick.team,
                    description=f"{kick.team}: {kick.description} (karny #{kick.kick_number})",
                    home_score=home_score,
                    away_score=away_score,
                    extra={"penalty_kick": kick.kick_number},
                )
            )
        decided_by = "penalties"
        is_draw = False
    elif tournament_settings.extra_time:
        events.append(
            MatchEvent(
                minute=90,
                phase="extra_first",
                event_type="phase_start",
                team=None,
                description="Dogrywka — pierwsza połowa (91–105')",
                home_score=home_score,
                away_score=away_score,
            )
        )

        golden_goal_scored = False
        for phase, start, end in (("extra_first", 91, 105), ("extra_second", 106, 120)):
            if golden_goal_scored:
                break
            if phase == "extra_second":
                events.append(
                    MatchEvent(
                        minute=105,
                        phase="extra_second",
                        event_type="phase_start",
                        team=None,
                        description="Dogrywka — druga połowa (106–120')",
                        home_score=home_score,
                        away_score=away_score,
                    )
                )

            period_goals = _simulate_period_goals(
                rng, home_team, away_team,
                home_rating, away_rating,
                phase, start, end,
            )

            for minute, team in period_goals:
                if team == home_team:
                    home_score += 1
                else:
                    away_score += 1
                is_golden_goal = tournament_settings.golden_goal
                event_type = "golden_goal" if is_golden_goal else "goal"
                description = _goal_description(
                    team, minute, phase, home_score, away_score, is_golden_goal
                )
                if is_golden_goal:
                    golden_goal_scored = True

                events.append(
                    MatchEvent(
                        minute=minute,
                        phase=phase,
                        event_type=event_type,
                        team=team,
                        description=description,
                        home_score=home_score,
                        away_score=away_score,
                    )
                )
                if golden_goal_scored:
                    break

        events.append(
            MatchEvent(
                minute=120,
                phase="extra_second",
                event_type="full_time",
                team=None,
                description=f"Koniec dogrywki: {home_score}:{away_score}",
                home_score=home_score,
                away_score=away_score,
            )
        )

        if home_score != away_score:
            winner = home_team if home_score > away_score else away_team
            decided_by = "golden_goal" if tournament_settings.golden_goal and golden_goal_scored else "extra_time"
            is_draw = False
        else:
            events.append(
                MatchEvent(
                    minute=120,
                    phase="penalties",
                    event_type="phase_start",
                    team=None,
                    description="Nadal remis — seria rzutów karnych!",
                    home_score=home_score,
                    away_score=away_score,
                )
            )
            penalty_shootout, winner, home_pen_score, away_pen_score = _simulate_penalty_shootout(
                rng, home_team, away_team, team_ratings
            )
            for kick in penalty_shootout:
                events.append(
                    MatchEvent(
                        minute=120,
                        phase="penalties",
                        event_type="penalty_goal" if kick.scored else "penalty_miss",
                        team=kick.team,
                        description=f"{kick.team}: {kick.description} (karny #{kick.kick_number})",
                        home_score=home_score,
                        away_score=away_score,
                        extra={"penalty_kick": kick.kick_number},
                    )
                )
            decided_by = "penalties"
            is_draw = False

    timeline_summary = _build_timeline_summary(events, home_team, away_team)

    return MatchResult(
        home_team=home_team,
        away_team=away_team,
        mode=mode.value,
        settings=asdict(tournament_settings),
        home_score_90=home_score_90,
        away_score_90=away_score_90,
        home_score_final=home_score,
        away_score_final=away_score,
        home_score_penalties=home_pen_score,
        away_score_penalties=away_pen_score,
        winner=winner,
        is_draw=is_draw and mode == MatchMode.FRIENDLY.value,
        decided_by=decided_by,
        events=events,
        penalty_shootout=penalty_shootout,
        timeline_summary=timeline_summary,
    )


def _build_timeline_summary(events: list[MatchEvent], home_team: str, away_team: str) -> str:
    goal_events = [event for event in events if event.event_type in ("goal", "golden_goal")]
    if not goal_events:
        return "Mecz bez bramek w regulaminowym czasie i dogrywce."

    parts = []
    for event in goal_events:
        marker = "ZG" if event.event_type == "golden_goal" else "G"
        parts.append(f"{marker} {event.minute}' {event.team}")
    return " | ".join(parts)


def format_match_text(result: MatchResult, animate: bool = False, delay: float = 0.0) -> str:
    """Formatuje przebieg meczu jako tekst (opcjonalnie z opóźnieniem dla terminala)."""
    import time

    lines = [
        f"{'=' * 56}",
        f"  {result.home_team}  vs  {result.away_team}",
        f"  Tryb: {result.mode} | Rozstrzygnięcie: {result.decided_by}",
        f"{'=' * 56}",
        "",
    ]

    for event in result.events:
        if event.event_type in ("kickoff", "goal", "golden_goal", "full_time", "phase_start",
                                "penalty_goal", "penalty_miss"):
            prefix = {
                "kickoff": ">>",
                "goal": "GOL",
                "golden_goal": "ZG!",
                "full_time": "FT",
                "phase_start": "..",
                "penalty_goal": "K+",
                "penalty_miss": "K-",
            }.get(event.event_type, "  ")
            score = f" [{event.home_score}:{event.away_score}]"
            lines.append(f"  {prefix} {event.description}{score}")
            if animate and delay > 0:
                time.sleep(delay)

    lines.append("")
    lines.append(f"  WYNIK KOŃCOWY: {result.home_score_final}:{result.away_score_final}")
    if result.home_score_penalties is not None:
        lines.append(
            f"  Karne: {result.home_score_penalties}:{result.away_score_penalties}"
        )
    if result.winner:
        lines.append(f"  ZWYCIĘZCA: {result.winner}")
    elif result.is_draw:
        lines.append("  REMIS (mecz towarzyski)")
    lines.append(f"{'=' * 56}")
    return "\n".join(lines)
