import unittest
import app.server

REDIS_HOST = '192.168.20.50'


class TestServer(unittest.TestCase):
    def test_redis_connection(self):
        """Test that the Battleship server can correctly find a Redis
        instance.

        Please note that this test only works if a Redis host is
        available (see REDIS_HOST above).
        """
        with app.server.Battleship(REDIS_HOST, db=1) as battleship:
            self.assertTrue(battleship.ping_redis())
