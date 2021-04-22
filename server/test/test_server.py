import unittest
import server

REDIS_HOST = 'localhost'


class TestServer(unittest.TestCase):
    """Please note that the tests in this suite only work if a Redis
    host is available (see REDIS_HOST above).
    """
    def test_redis_connection(self):
        """Test that the Battleship server can correctly find a Redis
        instance.
        """
        battleship = server.Battleship(REDIS_HOST, db=1)
        self.assertTrue(battleship.ping_redis())
