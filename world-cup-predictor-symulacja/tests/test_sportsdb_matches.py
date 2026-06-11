"""Testy pobierania meczów z TheSportsDB (mock + seed fallback)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import api
import sportsdb_client as sdb

ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = ROOT / "data" / "matches_seed.json"
CACHE_PATH = ROOT / "data" / "matches_cache.json"


class TestSportsdbMatches(unittest.TestCase):
    def setUp(self) -> None:
        self._cache_backup = CACHE_PATH.read_text(encoding="utf-8") if CACHE_PATH.exists() else None

    def tearDown(self) -> None:
        if self._cache_backup is None:
            if CACHE_PATH.exists():
                CACHE_PATH.unlink()
        else:
            CACHE_PATH.write_text(self._cache_backup, encoding="utf-8")

    def test_event_to_match_parses_scores(self) -> None:
        raw = {
            "idEvent": "99",
            "strHomeTeam": "Poland",
            "strAwayTeam": "Mexico",
            "intHomeScore": "2",
            "intAwayScore": "1",
            "strStatus": "FT",
            "dateEvent": "2026-06-11",
            "strTime": "18:00:00",
            "strLeague": "Test League",
            "idLeague": "1",
        }
        match = sdb._event_to_match(raw)
        self.assertEqual(match["home_score"], 2)
        self.assertEqual(match["away_score"], 1)
        self.assertTrue(match["is_finished"])

    def test_build_timeline_from_api_goals(self) -> None:
        entries = [
            {
                "strTimeline": "Goal",
                "intTime": "10",
                "strHome": "Yes",
                "strTeam": "Poland",
                "strPlayer": "Lewandowski",
                "strAssist": "",
            },
            {
                "strTimeline": "Goal",
                "intTime": "55",
                "strHome": "No",
                "strTeam": "Mexico",
                "strPlayer": "Lozano",
                "strAssist": "",
            },
        ]
        events = sdb._build_timeline_from_api(entries, "Poland", "Mexico", 1, 1)
        goals = [e for e in events if e["event_type"] == "goal"]
        self.assertEqual(len(goals), 2)
        self.assertEqual(goals[-1]["home_score"], 1)
        self.assertEqual(goals[-1]["away_score"], 1)

    @patch.object(sdb, "_api_get", return_value=None)
    def test_get_matches_today_seed_fallback(self, _mock_api: object) -> None:
        matches, source, date = sdb.get_matches_today(date_str="2026-06-11", force_refresh=True)
        self.assertEqual(source, "seed")
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(date)

    @patch.object(sdb, "_fetch_events_for_date")
    @patch.object(sdb, "_fetch_upcoming_from_api")
    def test_refresh_matches_cache_writes_file(
        self,
        mock_upcoming: object,
        mock_today: object,
    ) -> None:
        mock_today.return_value = [{
            "id": "api-1",
            "home_team": "Brazil",
            "away_team": "Germany",
            "home_badge": None,
            "away_badge": None,
            "date": "2026-06-11",
            "time": "20:00:00",
            "league": "Test",
            "league_id": "1",
            "status": "NS",
            "home_score": None,
            "away_score": None,
            "is_finished": False,
            "is_upcoming": True,
            "is_live": False,
            "venue": "",
            "source": "thesportsdb",
        }]
        mock_upcoming.return_value = []

        cache = sdb.refresh_matches_cache("2026-06-11")
        self.assertTrue(CACHE_PATH.exists())
        self.assertEqual(cache["today"]["source"], "thesportsdb")
        self.assertEqual(len(cache["today"]["matches"]), 1)

    def test_cache_is_fresh(self) -> None:
        fresh = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.assertTrue(sdb._cache_is_fresh(fresh))
        stale = {"updated_at": "2020-01-01T00:00:00+00:00"}
        self.assertFalse(sdb._cache_is_fresh(stale))

    def test_get_match_timeline_seed(self) -> None:
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        event_id = next(iter(seed.get("timelines", {}).keys()))
        with patch.object(sdb, "_api_get", return_value=None):
            events, source = sdb.get_match_timeline(event_id)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]["event_type"], "kickoff")
        self.assertEqual(source, "seed")

    def test_build_timeline_from_score_fallback(self) -> None:
        events = sdb._build_timeline_from_score_fallback("Team A", "Team B", 2, 1)
        goals = [e for e in events if e["event_type"] == "goal"]
        self.assertEqual(len(goals), 3)
        self.assertEqual(events[-1]["home_score"], 2)
        self.assertEqual(events[-1]["away_score"], 1)

    def test_get_match_timeline_score_fallback(self) -> None:
        match = {
            "home_team": "Monterey Bay FC",
            "away_team": "Sporting JAX",
            "home_score": 2,
            "away_score": 1,
            "is_finished": True,
            "is_live": False,
        }
        with patch.object(sdb, "_api_get", return_value={"timeline": None}):
            events, source = sdb.get_match_timeline("2397164", match=match)
        self.assertEqual(source, "score_fallback")
        self.assertGreaterEqual(len(events), 3)
        self.assertEqual(events[0]["event_type"], "kickoff")

    def test_resolve_simulation_team_name(self) -> None:
        self.assertEqual(sdb.resolve_simulation_team_name("Poland"), "Poland")
        self.assertEqual(sdb.resolve_simulation_team_name("USA"), "United States")

    @patch.object(api, "get_matches_today")
    def test_api_matches_endpoint(self, mock_today: object) -> None:
        mock_today.return_value = ([{"id": "1", "home_team": "A", "away_team": "B"}], "seed", "2026-06-11")
        body = api.matches_list(date=None)
        self.assertEqual(body["count"], 1)
        self.assertIn("free_tier_note", body)

    @patch.object(api, "get_upcoming_matches")
    def test_api_upcoming_endpoint(self, mock_upcoming: object) -> None:
        mock_upcoming.return_value = ([{"id": "2"}], "seed")
        body = api.matches_upcoming(league_id=None)
        self.assertEqual(body["count"], 1)

    @patch.object(api, "get_match_details")
    @patch.object(api, "get_match_timeline")
    def test_api_timeline_endpoint(self, mock_tl: object, mock_details: object) -> None:
        mock_details.return_value = {
            "id": "seed-001",
            "home_team": "Mexico",
            "away_team": "South Africa",
            "home_score": 2,
            "away_score": 0,
            "source": "seed",
        }
        mock_tl.return_value = ([{"minute": 9, "event_type": "goal", "description": "Gol"}], "seed")
        body = api.match_timeline("seed-001")
        self.assertEqual(len(body["events"]), 1)
        self.assertEqual(body["timeline_source"], "seed")

    @patch.object(api, "get_match_details")
    def test_api_match_details_endpoint(self, mock_details: object) -> None:
        mock_details.return_value = {
            "id": "seed-001",
            "home_team": "Poland",
            "away_team": "Mexico",
            "home_score": None,
            "away_score": None,
            "source": "seed",
        }
        body = api.match_details("seed-001", timeline=False)
        self.assertEqual(body["match"]["home_team"], "Poland")
        self.assertIn("simulation_teams", body)


if __name__ == "__main__":
    unittest.main()
