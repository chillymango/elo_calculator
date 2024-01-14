import os
import threading
import time
import unittest

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from server.core.app import create_app
from server.core.database import init_db, get_sessionlocal
from server.core.dependencies import get_game_manager
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
        self.game = self.game_manager.create_game()

    def _receive_state_message(self, ws, timeout: float = 1.0, fail_on_missing: bool = True):
        return ws.receive_json()  # Timeout in seconds

    def test_handshake_and_initial_receive(self):
        with self.client.websocket_connect(f"/api/game/{str(self.game.uuid)}/ws?token={self.token}") as ws:
            self._receive_state_message(ws)
            ws.close()

    def test_handshake_and_throw_garbage_is_ok(self):
        with self.client.websocket_connect(f"/api/game/{str(self.game.uuid)}/ws?token={self.token}") as ws:
            self._receive_state_message(ws)
            ws.send_json({"garbage": True})
            ws.send_json({"garbage": True})
            ws.send_json({"garbage": True})
            ws.close()

    def test_handshake_and_spectator(self):
        with self.client.websocket_connect(f"/api/game/{str(self.game.uuid)}/ws?token={self.token}") as ws:
            self._receive_state_message(ws)
            with self.game_manager.game_context(self.game.uuid) as game:
                game.play_white(2, 0, 2)
            self._receive_state_message(ws)
            with self.game_manager.game_context(self.game.uuid) as game:
                game.play_black(2, 1, 2)

            # TODO: try to send a game command over the websocket and make sure it doesn't work

    def test_multiple_spectators(self):
        threads: list[threading.Thread] = []
        for _ in range(5):
            t = threading.Thread(target=self.test_handshake_and_spectator)
            t.start()
            threads.append(t)

        for t in threads:
            t.join(timeout=3.0)

    def test_create_game_and_join_with_code(self):
        pass


if __name__ == "__main__":
    unittest.main()
