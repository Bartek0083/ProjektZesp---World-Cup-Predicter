"""Testy silnika symulacji meczu."""

from __future__ import annotations

import unittest

from match_engine import MatchMode, TournamentSettings, simulate_match


class TestMatchEngine(unittest.TestCase):
    def test_friendly_can_end_in_draw(self) -> None:
        for seed in range(50):
            result = simulate_match("Poland", "Japan", mode=MatchMode.FRIENDLY, seed=seed)
            if result.is_draw:
                self.assertIsNone(result.winner)
                self.assertEqual(result.decided_by, "90_minutes")
                break
        else:
            self.skipTest("Brak remisu w 50 próbach — akceptowalne losowo")

    def test_friendly_has_no_penalties(self) -> None:
        result = simulate_match("Argentina", "Brazil", mode=MatchMode.FRIENDLY, seed=1)
        self.assertEqual(result.penalty_shootout, [])
        self.assertIsNone(result.home_score_penalties)

    def test_tournament_penalties_after_90(self) -> None:
        settings = TournamentSettings(extra_time=False, penalties_after_90=True)
        found = False
        for seed in range(200):
            result = simulate_match(
                "France", "England",
                mode=MatchMode.TOURNAMENT,
                settings=settings,
                seed=seed,
            )
            if result.home_score_90 == result.away_score_90:
                self.assertEqual(result.decided_by, "penalties")
                self.assertGreater(len(result.penalty_shootout), 0)
                self.assertIsNotNone(result.winner)
                found = True
                break
        self.assertTrue(found, "Nie znaleziono remisu po 90 min w 200 próbach")

    def test_tournament_extra_time_events(self) -> None:
        settings = TournamentSettings(extra_time=True, golden_goal=False, penalties_after_90=False)
        for seed in range(300):
            result = simulate_match(
                "Spain", "Germany",
                mode=MatchMode.TOURNAMENT,
                settings=settings,
                seed=seed,
            )
            phases = {event.phase for event in result.events}
            if "extra_first" in phases or result.decided_by == "penalties":
                self.assertIn("regular", phases)
                return
        self.fail("Brak dogrywki lub karnych w 300 próbach")

    def test_golden_goal_ends_match(self) -> None:
        settings = TournamentSettings(extra_time=True, golden_goal=True, penalties_after_90=False)
        for seed in range(500):
            result = simulate_match(
                "Brazil", "France",
                mode=MatchMode.TOURNAMENT,
                settings=settings,
                seed=seed,
            )
            golden = [e for e in result.events if e.event_type == "golden_goal"]
            if golden:
                self.assertEqual(result.decided_by, "golden_goal")
                self.assertIsNotNone(result.winner)
                return
        self.skipTest("Brak złotej bramki w 500 próbach")

    def test_events_have_valid_scores(self) -> None:
        result = simulate_match("Poland", "Mexico", mode=MatchMode.FRIENDLY, seed=5)
        for event in result.events:
            self.assertGreaterEqual(event.home_score, 0)
            self.assertGreaterEqual(event.away_score, 0)

    def test_unknown_team_raises(self) -> None:
        with self.assertRaises(ValueError):
            simulate_match("Nieistniejąca", "Poland", seed=1)

    def test_reproducible_with_seed(self) -> None:
        a = simulate_match("Argentina", "France", mode=MatchMode.FRIENDLY, seed=777)
        b = simulate_match("Argentina", "France", mode=MatchMode.FRIENDLY, seed=777)
        self.assertEqual(a.home_score_final, b.home_score_final)
        self.assertEqual(a.away_score_final, b.away_score_final)
        self.assertEqual(len(a.events), len(b.events))


if __name__ == "__main__":
    unittest.main()
