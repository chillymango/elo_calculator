import os
import time
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

from server.core.app import create_app
from server.core.database import init_db, get_sessionlocal
from server.core import env
from server.models.dto.match import MatchResult
from server.models.dto.player import AddPlayer, ListPlayersResponse
from server.models.dto.summary import Summary, SummaryResponseDto
from server.models.orm.match import Match
from server.models.orm.player import Player
from server.utils import path_util


class TestCalculatorServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.exists(path_util.TEST_DATABASE):
            os.remove(path_util.TEST_DATABASE)
        super().setUpClass()
        os.environ['TESTING'] = '1'
        cls.app = create_app()
        cls.engine = init_db()
        cls.session: Session = get_sessionlocal()()
        cls.client = TestClient(cls.app)

    def get_players(self) -> ListPlayersResponse:
        response = self.client.get("/players")
        response.raise_for_status()
        return ListPlayersResponse.parse_raw(response.content)

    def get_summary(self) -> Summary:
        r = self.client.get("/summary")
        r.raise_for_status()
        summary_response_dto = SummaryResponseDto.parse_raw(r.content)
        return Summary.parse_raw(summary_response_dto.response_json_str)

    def test_add_players_and_get_elo_scores(self) -> None:
        players = self.get_players()
        for player_name in ("albert", "alex", "brian", "dan", "sam"):
            add_player = AddPlayer(name=player_name)
            r = self.client.post("/add_player", json=add_player.dict())
            r.raise_for_status()
        players = self.get_players()
        self.assertEqual(len(players.players), 5)

        # add some matches and verify basic tabulations
        for winner, loser in (
            ("brian", "albert"),
            ("alex", "albert"),
            ("sam", "albert"),
            ("brian", "sam")
        ):
            match_dto = MatchResult(winner=winner, loser=loser)
            r = self.client.post("/match", json=match_dto.dict())
            r.raise_for_status()
        albert = self.session.query(Player).filter(Player.name == "albert").one()
        self.assertEqual(len(albert.won_matches), 0)
        self.assertEqual(len(albert.lost_matches), 3)
        brian = self.session.query(Player).filter(Player.name == "brian").one()
        self.assertEqual(len(brian.won_matches), 2)
        self.assertEqual(len(brian.lost_matches), 0)

        # access the summary endpoint and make sure things look roughly correct
        summary = self.get_summary()
        breakpoint()

    def test_login_success(self):
        form = {"grant_type": "password", "username": env.AUTH_USERNAME, "password": env.AUTH_PASSWORD}
        r = self.client.post("/token", data=form)
        r.raise_for_status()

    def test_login_fail(self):
        with self.assertRaises(Exception):
            form = {"grant_type": "password", "username": "fakeuser", "password": "fakepass"}
            self.client.post("/token", data=form).raise_for_status()

    def tearDown(self):
        self.session.query(Player).delete()
        self.session.query(Match).delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.engine.dispose()


if __name__ == "__main__":
    unittest.main()
