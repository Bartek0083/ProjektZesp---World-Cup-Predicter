#!/usr/bin/env python3
"""Generuje wykresy do sprawozdania na podstawie danych z modułu symulacji."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from match_engine import MatchMode, simulate_match
from predictions import _poisson_pmf, compute_match_preview

OUTPUT_DIR = Path(__file__).resolve().parent / "docs" / "wykresy"


def _ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def chart_poisson_xg(home: str, away: str) -> Path:
    """Rozkład Poissona liczby bramek (xG) — predictions.py."""
    preview = compute_match_preview(home, away)
    home_xg = preview["home"]["expected_goals"]
    away_xg = preview["away"]["expected_goals"]
    goals = np.arange(0, 7)

    home_p = [_poisson_pmf(int(g), home_xg) * 100 for g in goals]
    away_p = [_poisson_pmf(int(g), away_xg) * 100 for g in goals]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    width = 0.35
    x = np.arange(len(goals))
    ax.bar(x - width / 2, home_p, width, label=f"{home} (xG={home_xg})", color="#c8102e")
    ax.bar(x + width / 2, away_p, width, label=f"{away} (xG={away_xg})", color="#000000")
    ax.set_xlabel("Liczba bramek")
    ax.set_ylabel("Prawdopodobieństwo (%)")
    ax.set_title(f"Rozkład Poissona bramek — {home} vs {away}")
    ax.set_xticks(x)
    ax.set_xticklabels(goals)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = _ensure_output_dir() / "wykres_poisson_xg.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_outcome_probs(home: str, away: str) -> Path:
    """Słupki 1 / X / 2 — compute_match_preview()."""
    preview = compute_match_preview(home, away)
    probs = preview["probabilities"]
    labels = ["1 (gospodarze)", "X (remis)", "2 (goście)"]
    values = [probs["home_win"], probs["draw"], probs["away_win"]]
    colors = ["#2e7d32", "#757575", "#1565c0"]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Prawdopodobieństwo (%)")
    ax.set_title(f"Szacunek 1/X/2 — {home} vs {away}")
    ax.set_ylim(0, max(values) * 1.25)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val}%", ha="center", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = _ensure_output_dir() / "wykres_1x2.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_monte_carlo_convergence(
    home: str,
    away: str,
    *,
    max_sims: int = 500,
    step: int = 10,
) -> Path:
    """
    Zbieżność Monte Carlo — jak rośnie liczba symulacji,
    stabilizuje się szacowane P(zwycięstwo gospodarzy).
    Nie jest to krzywa uczenia ML, ale realny wykres z match_engine.
    """
    wins = 0
    xs: list[int] = []
    ys: list[float] = []

    for seed in range(max_sims):
        result = simulate_match(home, away, mode=MatchMode.FRIENDLY, seed=seed)
        if result.winner == home:
            wins += 1
        n = seed + 1
        if n % step == 0 or n == max_sims:
            xs.append(n)
            ys.append(wins / n * 100)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(xs, ys, color="#1b5e20", linewidth=2, label="P(zwycięstwo gospodarzy)")
    ax.axhline(ys[-1], color="#ef6c00", linestyle="--", linewidth=1, label=f"wartość po {max_sims} symulacjach: {ys[-1]:.1f}%")
    ax.set_xlabel("Liczba symulacji")
    ax.set_ylabel("Skumulowane P(zwycięstwo) (%)")
    ax.set_title(f"Zbieżność Monte Carlo — {home} vs {away} (tryb towarzyski)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = _ensure_output_dir() / "wykres_zbieznosc_monte_carlo.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_goals_timeline(home: str, away: str, seed: int) -> Path:
    """Bramki w czasie z jednej symulacji (demo_terminal)."""
    result = simulate_match(home, away, mode=MatchMode.FRIENDLY, seed=seed)
    goals = [e for e in result.events if e.event_type == "goal"]

    fig, ax = plt.subplots(figsize=(9, 3.5))
    for event in goals:
        color = "#c8102e" if event.team == home else "#1565c0"
        y = 1 if event.team == home else 0
        ax.scatter(event.minute, y, s=120, color=color, zorder=3)
        ax.annotate(f"{event.minute}'", (event.minute, y), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)

    ax.set_yticks([0, 1])
    ax.set_yticklabels([away, home])
    ax.set_xlabel("Minuta meczu")
    ax.set_title(f"Timeline bramek — {home} {result.home_score_final}:{result.away_score_final} {away} (seed={seed})")
    ax.set_xlim(-2, 95)
    ax.axvline(45, color="#888", linestyle=":", alpha=0.7, label="przerwa")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    path = _ensure_output_dir() / "wykres_bramki_czas.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    paths = [
        chart_poisson_xg("Poland", "Germany"),
        chart_outcome_probs("Poland", "Germany"),
        chart_monte_carlo_convergence("Argentina", "Brazil", max_sims=500),
        chart_goals_timeline("Argentina", "Brazil", seed=42),
    ]
    print("Wygenerowano wykresy:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
