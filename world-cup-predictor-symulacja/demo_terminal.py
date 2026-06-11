#!/usr/bin/env python3
"""Demo symulacji meczu w terminalu — cztery scenariusze testowe."""

from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from match_engine import MatchMode, TournamentSettings, format_match_text, simulate_match


def run_demo(animate: bool = False, delay: float = 0.15) -> None:
    scenarios = [
        {
            "title": "1. Mecz towarzyski — Argentyna vs Brazylia",
            "home": "Argentina",
            "away": "Brazil",
            "mode": MatchMode.FRIENDLY,
            "settings": None,
            "seed": 42,
        },
        {
            "title": "2. Mecz turniejowy — dogrywka + karne",
            "home": "France",
            "away": "England",
            "mode": MatchMode.TOURNAMENT,
            "settings": TournamentSettings(extra_time=True, golden_goal=False, penalties_after_90=False),
            "seed": 7,
        },
        {
            "title": "3. Mecz turniejowy — złota bramka w dogrywce",
            "home": "Spain",
            "away": "Germany",
            "mode": MatchMode.TOURNAMENT,
            "settings": TournamentSettings(extra_time=True, golden_goal=True, penalties_after_90=False),
            "seed": 99,
        },
        {
            "title": "4. Mecz turniejowy — karne po 90 minutach",
            "home": "Portugal",
            "away": "Netherlands",
            "mode": MatchMode.TOURNAMENT,
            "settings": TournamentSettings(extra_time=False, golden_goal=False, penalties_after_90=True),
            "seed": 0,
        },
    ]

    for scenario in scenarios:
        print(f"\n{scenario['title']}\n")
        result = simulate_match(
            home_team=scenario["home"],
            away_team=scenario["away"],
            mode=scenario["mode"],
            settings=scenario["settings"],
            seed=scenario["seed"],
        )
        print(format_match_text(result, animate=animate, delay=delay))
        print(f"  Podsumowanie bramek: {result.timeline_summary}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo symulacji meczu piłkarskiego")
    parser.add_argument("--animate", action="store_true", help="Animacja z opóźnieniem między zdarzeniami")
    parser.add_argument("--delay", type=float, default=0.12, help="Opóźnienie animacji (s)")
    args = parser.parse_args()
    run_demo(animate=args.animate, delay=args.delay)


if __name__ == "__main__":
    main()
