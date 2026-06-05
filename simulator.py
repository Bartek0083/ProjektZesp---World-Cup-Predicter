from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from data import load_group_matches, missing_teams, normalize_team_name
from model import TrainedWorldCupModel, predict_match_proba


OUTCOMES = np.array(["home_win", "draw", "away_win"])

R32_SLOTS = [
    {"match_id": "R32_01", "home_slot": "2A", "away_slot": "2B"},
    {"match_id": "R32_02", "home_slot": "1C", "away_slot": "2F"},
    {"match_id": "R32_03", "home_slot": "1E", "away_slot": "3ABCDF"},
    {"match_id": "R32_04", "home_slot": "1F", "away_slot": "2C"},
    {"match_id": "R32_05", "home_slot": "2E", "away_slot": "2I"},
    {"match_id": "R32_06", "home_slot": "1I", "away_slot": "3CDFGH"},
    {"match_id": "R32_07", "home_slot": "1A", "away_slot": "3CEFHI"},
    {"match_id": "R32_08", "home_slot": "1L", "away_slot": "3EHIJK"},
    {"match_id": "R32_09", "home_slot": "1G", "away_slot": "3AEHIJ"},
    {"match_id": "R32_10", "home_slot": "1D", "away_slot": "3BEFIJ"},
    {"match_id": "R32_11", "home_slot": "1H", "away_slot": "2J"},
    {"match_id": "R32_12", "home_slot": "2K", "away_slot": "2L"},
    {"match_id": "R32_13", "home_slot": "1B", "away_slot": "3EFGIJ"},
    {"match_id": "R32_14", "home_slot": "2D", "away_slot": "2G"},
    {"match_id": "R32_15", "home_slot": "1J", "away_slot": "2H"},
    {"match_id": "R32_16", "home_slot": "1K", "away_slot": "3DEIJL"},
]

R16_MAPPING = [
    ("R16_01", "R32_03", "R32_06"),
    ("R16_02", "R32_01", "R32_04"),
    ("R16_03", "R32_02", "R32_05"),
    ("R16_04", "R32_07", "R32_08"),
    ("R16_05", "R32_12", "R32_11"),
    ("R16_06", "R32_10", "R32_09"),
    ("R16_07", "R32_15", "R32_14"),
    ("R16_08", "R32_13", "R32_16"),
]

QF_MAPPING = [
    ("QF_01", "R16_01", "R16_02"),
    ("QF_02", "R16_05", "R16_06"),
    ("QF_03", "R16_03", "R16_04"),
    ("QF_04", "R16_07", "R16_08"),
]

SF_MAPPING = [
    ("SF_01", "QF_01", "QF_02"),
    ("SF_02", "QF_03", "QF_04"),
]

FINAL_MAPPING = [("FINAL", "SF_01", "SF_02")]


def get_rng(seed: int | None = None, rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng(seed)


def validate_group_matches(
    group_matches: pd.DataFrame,
    trained_model: TrainedWorldCupModel,
) -> pd.DataFrame:
    required_columns = ["group", "home_team", "away_team"]
    missing_columns = [column for column in required_columns if column not in group_matches.columns]
    if missing_columns:
        raise ValueError(f"Group matches are missing required columns: {missing_columns}")

    group_matches = group_matches[required_columns].copy()
    group_matches["group"] = group_matches["group"].astype(str).str.strip()
    group_matches["home_team"] = (
        group_matches["home_team"].astype(str).str.strip().apply(normalize_team_name)
    )
    group_matches["away_team"] = (
        group_matches["away_team"].astype(str).str.strip().apply(normalize_team_name)
    )

    teams = pd.concat([group_matches["home_team"], group_matches["away_team"]]).unique()
    unavailable = missing_teams(teams, trained_model.latest_team_data)
    if unavailable:
        raise ValueError(f"Missing ranking data for teams: {unavailable}")

    return group_matches


def simulate_match(
    trained_model: TrainedWorldCupModel,
    home_team: str,
    away_team: str,
    tournament: str = "FIFA World Cup",
    neutral: int = 1,
    rng: np.random.Generator | None = None,
) -> dict[str, float | str]:
    rng = get_rng(rng=rng)
    proba = predict_match_proba(
        trained_model=trained_model,
        home_team=home_team,
        away_team=away_team,
        tournament=tournament,
        neutral=neutral,
    )

    probabilities = np.array([proba["home_win"], proba["draw"], proba["away_win"]], dtype=float)
    result = rng.choice(OUTCOMES, p=probabilities)

    return {
        "home_team": str(proba["home_team"]),
        "away_team": str(proba["away_team"]),
        "result": str(result),
        "home_win_proba": float(proba["home_win"]),
        "draw_proba": float(proba["draw"]),
        "away_win_proba": float(proba["away_win"]),
    }


def test_match_simulation(
    trained_model: TrainedWorldCupModel,
    home_team: str,
    away_team: str,
    n_simulations: int = 10_000,
    seed: int | None = None,
) -> pd.DataFrame:
    rng = get_rng(seed=seed)
    proba = predict_match_proba(trained_model, home_team, away_team)
    probabilities = np.array([proba["home_win"], proba["draw"], proba["away_win"]], dtype=float)

    simulated_results = rng.choice(OUTCOMES, size=n_simulations, p=probabilities)
    simulation_summary = (
        pd.Series(simulated_results)
        .value_counts(normalize=True)
        .reindex(OUTCOMES, fill_value=0)
        .mul(100)
        .round(2)
    )
    model_proba = pd.Series(probabilities * 100, index=OUTCOMES).round(2)

    return pd.DataFrame(
        {
            "model_probability_%": model_proba,
            "simulation_result_%": simulation_summary,
        }
    )


def add_probabilities_to_group_matches(
    trained_model: TrainedWorldCupModel,
    group_matches: pd.DataFrame,
    tournament: str = "FIFA World Cup",
    neutral: int = 1,
) -> pd.DataFrame:
    group_matches = validate_group_matches(group_matches, trained_model)
    rows = []

    for _, row in group_matches.iterrows():
        proba = predict_match_proba(
            trained_model=trained_model,
            home_team=row["home_team"],
            away_team=row["away_team"],
            tournament=tournament,
            neutral=neutral,
        )
        rows.append(
            {
                "group": row["group"],
                "home_team": proba["home_team"],
                "away_team": proba["away_team"],
                "home_win_proba": proba["home_win"],
                "draw_proba": proba["draw"],
                "away_win_proba": proba["away_win"],
            }
        )

    return pd.DataFrame(rows)


def simulate_one_group_stage(
    group_matches_with_proba: pd.DataFrame,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    rng = get_rng(rng=rng)
    match_results = []

    for _, row in group_matches_with_proba.iterrows():
        probabilities = np.array(
            [row["home_win_proba"], row["draw_proba"], row["away_win_proba"]],
            dtype=float,
        )
        result = rng.choice(OUTCOMES, p=probabilities)
        match_results.append(
            {
                "group": row["group"],
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "result": str(result),
                "home_win_proba": row["home_win_proba"],
                "draw_proba": row["draw_proba"],
                "away_win_proba": row["away_win_proba"],
            }
        )

    return pd.DataFrame(match_results)


def build_group_tables(
    match_results: pd.DataFrame,
    latest_team_data: pd.DataFrame,
) -> pd.DataFrame:
    teams = pd.concat(
        [
            match_results[["group", "home_team"]].rename(columns={"home_team": "team"}),
            match_results[["group", "away_team"]].rename(columns={"away_team": "team"}),
        ]
    ).drop_duplicates()

    table = teams.copy()
    table["points"] = 0
    table["wins"] = 0
    table["draws"] = 0
    table["losses"] = 0
    table["matches_played"] = 0
    table["fifa_points"] = table["team"].map(latest_team_data["fifa_points"])

    for _, match in match_results.iterrows():
        group = match["group"]
        home_team = match["home_team"]
        away_team = match["away_team"]
        result = match["result"]

        home_idx = (table["group"] == group) & (table["team"] == home_team)
        away_idx = (table["group"] == group) & (table["team"] == away_team)

        table.loc[home_idx, "matches_played"] += 1
        table.loc[away_idx, "matches_played"] += 1

        if result == "home_win":
            table.loc[home_idx, "points"] += 3
            table.loc[home_idx, "wins"] += 1
            table.loc[away_idx, "losses"] += 1
        elif result == "away_win":
            table.loc[away_idx, "points"] += 3
            table.loc[away_idx, "wins"] += 1
            table.loc[home_idx, "losses"] += 1
        elif result == "draw":
            table.loc[home_idx, "points"] += 1
            table.loc[away_idx, "points"] += 1
            table.loc[home_idx, "draws"] += 1
            table.loc[away_idx, "draws"] += 1
        else:
            raise ValueError(f"Unknown match result: {result}")

    table = table.sort_values(
        ["group", "points", "fifa_points"],
        ascending=[True, False, False],
    ).copy()
    table["group_position"] = table.groupby("group").cumcount() + 1
    return table


def get_group_stage_qualifiers(group_table: pd.DataFrame) -> pd.DataFrame:
    top_two = group_table[group_table["group_position"] <= 2].copy()
    third_places = group_table[group_table["group_position"] == 3].copy()
    best_third_places = third_places.sort_values(
        ["points", "fifa_points"],
        ascending=[False, False],
    ).head(8)

    qualifiers = pd.concat([top_two, best_third_places], ignore_index=True)
    qualifiers["qualified"] = 1
    return qualifiers


def summarize_group_stage(
    group_stage_simulations: pd.DataFrame,
    n_simulations: int,
) -> pd.DataFrame:
    summary = (
        group_stage_simulations.groupby(["team", "group"])
        .agg(
            avg_points=("points", "mean"),
            avg_wins=("wins", "mean"),
            avg_draws=("draws", "mean"),
            avg_losses=("losses", "mean"),
            group_winner_count=("group_position", lambda x: (x == 1).sum()),
            second_place_count=("group_position", lambda x: (x == 2).sum()),
            third_place_count=("group_position", lambda x: (x == 3).sum()),
            fourth_place_count=("group_position", lambda x: (x == 4).sum()),
            qualified_count=("qualified", "sum"),
        )
        .reset_index()
    )

    for column in ["avg_points", "avg_wins", "avg_draws", "avg_losses"]:
        summary[column] = summary[column].round(2)

    position_columns = {
        "group_winner_%": "group_winner_count",
        "second_place_%": "second_place_count",
        "third_place_%": "third_place_count",
        "fourth_place_%": "fourth_place_count",
        "qualified_%": "qualified_count",
    }
    for percent_column, count_column in position_columns.items():
        summary[percent_column] = (summary[count_column] / n_simulations * 100).round(2)

    return summary.sort_values(
        ["qualified_%", "group_winner_%", "avg_points"],
        ascending=[False, False, False],
    )


def simulate_group_stage_many_times(
    trained_model: TrainedWorldCupModel,
    group_matches: pd.DataFrame,
    n_simulations: int = 1_000,
    seed: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = get_rng(seed=seed)
    group_matches_with_proba = add_probabilities_to_group_matches(trained_model, group_matches)
    summary_rows = []

    for sim_id in range(1, n_simulations + 1):
        match_results = simulate_one_group_stage(group_matches_with_proba, rng=rng)
        group_table = build_group_tables(match_results, trained_model.latest_team_data)
        qualifiers = get_group_stage_qualifiers(group_table)
        qualified_teams = set(qualifiers["team"])

        for _, row in group_table.iterrows():
            summary_rows.append(
                {
                    "simulation_id": sim_id,
                    "group": row["group"],
                    "team": row["team"],
                    "group_position": row["group_position"],
                    "points": row["points"],
                    "wins": row["wins"],
                    "draws": row["draws"],
                    "losses": row["losses"],
                    "qualified": int(row["team"] in qualified_teams),
                }
            )

    simulations = pd.DataFrame(summary_rows)
    return summarize_group_stage(simulations, n_simulations), simulations, group_matches_with_proba


def simulate_knockout_match(
    trained_model: TrainedWorldCupModel,
    home_team: str,
    away_team: str,
    tournament: str = "FIFA World Cup",
    rng: np.random.Generator | None = None,
) -> dict[str, float | str]:
    rng = get_rng(rng=rng)
    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)
    match_res = simulate_match(
        trained_model=trained_model,
        home_team=home_team,
        away_team=away_team,
        tournament=tournament,
        neutral=1,
        rng=rng,
    )

    if match_res["result"] == "home_win":
        winner = home_team
        decided_by = "90_minutes"
    elif match_res["result"] == "away_win":
        winner = away_team
        decided_by = "90_minutes"
    else:
        home_points = trained_model.latest_team_data.loc[home_team, "fifa_points"]
        away_points = trained_model.latest_team_data.loc[away_team, "fifa_points"]
        home_penalty_chance = home_points / (home_points + away_points)
        winner = str(rng.choice([home_team, away_team], p=[home_penalty_chance, 1 - home_penalty_chance]))
        decided_by = "extra_time_or_penalties"

    return {
        "home_team": home_team,
        "away_team": away_team,
        "winner": winner,
        "result_90min": str(match_res["result"]),
        "decided_by": decided_by,
        "home_win_proba": float(match_res["home_win_proba"]),
        "draw_proba": float(match_res["draw_proba"]),
        "away_win_proba": float(match_res["away_win_proba"]),
    }


def get_team_from_direct_slot(group_table: pd.DataFrame, slot: str) -> str:
    position = int(slot[0])
    group = slot[1:]
    selected = group_table[
        (group_table["group"] == group) & (group_table["group_position"] == position)
    ]

    if selected.empty:
        raise ValueError(f"No team found for bracket slot: {slot}")

    return str(selected.iloc[0]["team"])


def find_valid_third_place_assignment(
    third_place_qualifiers: pd.DataFrame,
    third_place_slots: Iterable[str],
) -> dict[str, str]:
    third_teams = third_place_qualifiers.sort_values(
        ["points", "fifa_points"],
        ascending=[False, False],
    ).reset_index(drop=True)

    slots = list(third_place_slots)
    candidates_by_slot = {}

    for slot in slots:
        allowed_groups = list(slot[1:])
        candidates = third_teams[third_teams["group"].isin(allowed_groups)].copy()
        candidates_by_slot[slot] = candidates.sort_values(
            ["points", "fifa_points"],
            ascending=[False, False],
        ).to_dict("records")

    slots_sorted = sorted(slots, key=lambda slot: len(candidates_by_slot[slot]))
    assignment: dict[str, str] = {}
    used_teams: set[str] = set()

    def backtrack(slot_index: int) -> bool:
        if slot_index == len(slots_sorted):
            return True

        slot = slots_sorted[slot_index]
        for candidate in candidates_by_slot[slot]:
            team = candidate["team"]
            if team in used_teams:
                continue

            assignment[slot] = team
            used_teams.add(team)

            if backtrack(slot_index + 1):
                return True

            used_teams.remove(team)
            del assignment[slot]

        return False

    if not backtrack(0):
        debug_info = {
            slot: [{"group": candidate["group"], "team": candidate["team"]} for candidate in candidates]
            for slot, candidates in candidates_by_slot.items()
        }
        raise ValueError(f"Could not assign third-place teams to slots: {debug_info}")

    return assignment


def create_round_of_32_pairings_official(
    group_table: pd.DataFrame,
    qualifiers: pd.DataFrame,
) -> pd.DataFrame:
    third_place_qualifiers = qualifiers[qualifiers["group_position"] == 3].copy()
    third_place_qualifiers = third_place_qualifiers.sort_values(
        ["points", "fifa_points"],
        ascending=[False, False],
    )

    if len(third_place_qualifiers) != 8:
        raise ValueError(f"Expected 8 third-place qualifiers, got {len(third_place_qualifiers)}")

    third_place_slots = [
        match["away_slot"] for match in R32_SLOTS if str(match["away_slot"]).startswith("3")
    ]
    third_place_assignment = find_valid_third_place_assignment(
        third_place_qualifiers=third_place_qualifiers,
        third_place_slots=third_place_slots,
    )

    pairings = []
    for match in R32_SLOTS:
        home_slot = match["home_slot"]
        away_slot = match["away_slot"]

        if home_slot.startswith(("1", "2")):
            home_team = get_team_from_direct_slot(group_table, home_slot)
        elif home_slot.startswith("3"):
            home_team = third_place_assignment[home_slot]
        else:
            raise ValueError(f"Unknown home slot: {home_slot}")

        if away_slot.startswith(("1", "2")):
            away_team = get_team_from_direct_slot(group_table, away_slot)
        elif away_slot.startswith("3"):
            away_team = third_place_assignment[away_slot]
        else:
            raise ValueError(f"Unknown away slot: {away_slot}")

        pairings.append(
            {
                "round": "Round of 32",
                "match_id": match["match_id"],
                "home_slot": home_slot,
                "away_slot": away_slot,
                "home_team": home_team,
                "away_team": away_team,
            }
        )

    return pd.DataFrame(pairings)


def simulate_knockout_round(
    trained_model: TrainedWorldCupModel,
    pairings: pd.DataFrame,
    round_name: str,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    rng = get_rng(rng=rng)
    round_results = []

    for _, row in pairings.iterrows():
        match_result = simulate_knockout_match(
            trained_model=trained_model,
            home_team=row["home_team"],
            away_team=row["away_team"],
            tournament="FIFA World Cup",
            rng=rng,
        )
        round_results.append(
            {
                "round": round_name,
                "match_id": row["match_id"],
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "winner": match_result["winner"],
                "result_90min": match_result["result_90min"],
                "decided_by": match_result["decided_by"],
                "home_win_proba": match_result["home_win_proba"],
                "draw_proba": match_result["draw_proba"],
                "away_win_proba": match_result["away_win_proba"],
            }
        )

    return pd.DataFrame(round_results)


def create_pairings_from_winners(
    previous_results: pd.DataFrame,
    mapping: list[tuple[str, str, str]],
    round_name: str,
) -> pd.DataFrame:
    winners = previous_results.set_index("match_id")["winner"].to_dict()
    return pd.DataFrame(
        [
            {
                "round": round_name,
                "match_id": match_id,
                "home_team": winners[home_source],
                "away_team": winners[away_source],
                "home_source": home_source,
                "away_source": away_source,
            }
            for match_id, home_source, away_source in mapping
        ]
    )


def simulate_one_world_cup_official_bracket(
    trained_model: TrainedWorldCupModel,
    group_matches_with_proba: pd.DataFrame,
    rng: np.random.Generator | None = None,
) -> dict[str, pd.DataFrame | str]:
    rng = get_rng(rng=rng)

    group_match_results = simulate_one_group_stage(group_matches_with_proba, rng=rng)
    group_table = build_group_tables(group_match_results, trained_model.latest_team_data)
    qualifiers = get_group_stage_qualifiers(group_table)

    if len(qualifiers) != 32:
        raise ValueError(f"Expected 32 qualifiers, got {len(qualifiers)}")

    r32_pairings = create_round_of_32_pairings_official(group_table, qualifiers)
    r32_results = simulate_knockout_round(trained_model, r32_pairings, "Round of 32", rng=rng)

    r16_pairings = create_pairings_from_winners(r32_results, R16_MAPPING, "Round of 16")
    r16_results = simulate_knockout_round(trained_model, r16_pairings, "Round of 16", rng=rng)

    qf_pairings = create_pairings_from_winners(r16_results, QF_MAPPING, "Quarter-finals")
    qf_results = simulate_knockout_round(trained_model, qf_pairings, "Quarter-finals", rng=rng)

    sf_pairings = create_pairings_from_winners(qf_results, SF_MAPPING, "Semi-finals")
    sf_results = simulate_knockout_round(trained_model, sf_pairings, "Semi-finals", rng=rng)

    final_pairings = create_pairings_from_winners(sf_results, FINAL_MAPPING, "Final")
    final_results = simulate_knockout_round(trained_model, final_pairings, "Final", rng=rng)
    champion = str(final_results.iloc[0]["winner"])

    all_knockout_results = pd.concat(
        [r32_results, r16_results, qf_results, sf_results, final_results],
        ignore_index=True,
    )
    all_pairings = pd.concat(
        [r32_pairings, r16_pairings, qf_pairings, sf_pairings, final_pairings],
        ignore_index=True,
    )

    return {
        "champion": champion,
        "group_match_results": group_match_results,
        "group_table": group_table,
        "qualifiers": qualifiers,
        "pairings": all_pairings,
        "knockout_results": all_knockout_results,
    }


def simulate_world_cup_many_times_official_bracket(
    trained_model: TrainedWorldCupModel,
    group_matches: pd.DataFrame,
    n_simulations: int = 100,
    seed: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = get_rng(seed=seed)
    group_matches_with_proba = add_probabilities_to_group_matches(trained_model, group_matches)
    all_teams = pd.concat(
        [group_matches_with_proba["home_team"], group_matches_with_proba["away_team"]]
    ).unique()

    team_stats = {
        team: {
            "team": team,
            "round_of_32": 0,
            "round_of_16": 0,
            "quarter_final": 0,
            "semi_final": 0,
            "final": 0,
            "champion": 0,
        }
        for team in all_teams
    }
    knockout_rows = []

    for sim_id in range(1, n_simulations + 1):
        simulation = simulate_one_world_cup_official_bracket(
            trained_model=trained_model,
            group_matches_with_proba=group_matches_with_proba,
            rng=rng,
        )
        qualifiers = simulation["qualifiers"]
        knockout_results = simulation["knockout_results"]
        champion = simulation["champion"]

        for team in qualifiers["team"]:
            team_stats[team]["round_of_32"] += 1

        round_to_column = {
            "Round of 32": "round_of_16",
            "Round of 16": "quarter_final",
            "Quarter-finals": "semi_final",
            "Semi-finals": "final",
        }
        for round_name, column in round_to_column.items():
            winners = knockout_results[knockout_results["round"] == round_name]["winner"].tolist()
            for team in winners:
                team_stats[team][column] += 1

        team_stats[champion]["champion"] += 1
        knockout_copy = knockout_results.copy()
        knockout_copy["simulation_id"] = sim_id
        knockout_rows.append(knockout_copy)

    stats_df = pd.DataFrame(team_stats.values())
    for column in [
        "round_of_32",
        "round_of_16",
        "quarter_final",
        "semi_final",
        "final",
        "champion",
    ]:
        stats_df[f"{column}_%"] = (stats_df[column] / n_simulations * 100).round(2)

    stats_df = stats_df.sort_values(
        ["champion_%", "final_%", "semi_final_%", "quarter_final_%"],
        ascending=[False, False, False, False],
    )
    knockout_results = pd.concat(knockout_rows, ignore_index=True) if knockout_rows else pd.DataFrame()

    return stats_df, knockout_results, group_matches_with_proba


def simulate_default_group_stage(
    trained_model: TrainedWorldCupModel,
    data_dir: str | Path | None = None,
    n_simulations: int = 1_000,
    seed: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_matches = load_group_matches(data_dir=data_dir)
    return simulate_group_stage_many_times(
        trained_model=trained_model,
        group_matches=group_matches,
        n_simulations=n_simulations,
        seed=seed,
    )
