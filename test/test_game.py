import os
import threading
import time
import unittest

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from server.core.app import create_app
from server.core.database import init_db, get_sessionlocal
from server.core.dependencies import get_game_manager
from server.models.dto.game import CreateGameRequest, CreateGameResponse
from server.models.orm.game import GameState
from server.utils import path_util


class TestWebSocket(unittest.TestCase):

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

        cls.game_manager = get_game_manager()
        cls.token: str | None = None

    def login(self):
        resp = self.client.post("/api/login", json={"name": "test-user"})
        resp.raise_for_status()
        self.token = resp.json()["token"]
        self.client.headers = {'Authorization': f'Bearer {self.token}'}

    def setUp(self):
        # create new auth header for each test
        self.login()

    def create_game(self):
        create_resp = self.client.post("/api/game", json=CreateGameRequest().dict())
        create_resp.raise_for_status()
        game_response = CreateGameResponse.parse_raw(create_resp.content)
        get_resp = self.client.get(f"/api/game/{game_response.game_id}")
        get_resp.raise_for_status()
        return GameState.parse_raw(get_resp.content)

    def get_game_by_code(self, code: str):
        get_id_resp = self.client.get(f"/api/game/code?code={code}")
        get_id_resp.raise_for_status()
        game_id = get_id_resp.json()["game_id"]
        get_game_resp = self.client.get(f"/api/game/{game_id}")
        get_game_resp.raise_for_status()
        return GameState.parse_raw(get_game_resp.content)

    def test_create_game(self):
        self.create_game()

    def test_create_game_and_join_with_game_code(self):
        game = self.create_game()
        game_by_code = self.get_game_by_code(game.code)
        self.assertEqual(game.code, game_by_code.code)
        self.assertEqual(game.board, game_by_code.board)
        self.assertEqual(game.host_player_id, game_by_code.host_player_id)
        self.assertEqual(game.white_player_id, game_by_code.white_player_id)
        self.assertEqual(game.black_player_id, game_by_code.black_player_id)
        self.assertEqual(game.white_is_connected, game_by_code.white_is_connected)
        self.assertEqual(game.black_is_connected, game_by_code.black_is_connected)


if __name__ == "__main__":
    unittest.main()
