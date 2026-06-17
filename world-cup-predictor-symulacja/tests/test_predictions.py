"""Testy predykcji i statystyk."""

import unittest

from match_stats import aggregate_timeline_stats
from predictions import compare_real_vs_simulation, compute_match_preview


class TestPredictions(unittest.TestCase):
    def test_preview_probabilities_sum_near_100(self) -> None:
        preview = compute_match_preview("Argentina", "France")
        p = preview["probabilities"]
        total = p["home_win"] + p["draw"] + p["away_win"]
        self.assertGreater(total, 95)
        self.assertLess(total, 101)

    def test_preview_has_expected_goals(self) -> None:
        preview = compute_match_preview("Poland", "Germany")
        self.assertGreater(preview["home"]["expected_goals"], 0)
        self.assertIn("expected_score", preview)

    def test_compare_exact_match(self) -> None:
        c = compare_real_vs_simulation(2, 1, 2, 1)
        self.assertTrue(c["exact_score_match"])
        self.assertTrue(c["outcome_match"])

    def test_compare_outcome_only(self) -> None:
        c = compare_real_vs_simulation(2, 0, 1, 0)
        self.assertFalse(c["exact_score_match"])
        self.assertTrue(c["outcome_match"])


class TestMatchStats(unittest.TestCase):
    def test_aggregate_goals(self) -> None:
        events = [
            {"event_type": "goal", "team": "Poland", "minute": 23, "side": "home"},
            {"event_type": "goal", "team": "Germany", "minute": 67, "side": "away"},
        ]
        stats = aggregate_timeline_stats(events, "Poland", "Germany")
        self.assertEqual(stats["goals"]["home"], 1)
        self.assertEqual(stats["goals"]["away"], 1)
        self.assertEqual(len(stats["goal_minutes"]), 2)


if __name__ == "__main__":
    unittest.main()
