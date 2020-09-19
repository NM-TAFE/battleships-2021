import unittest
import app.game
import app.server

REDIS_HOST = '192.168.20.50'


class TestServer(unittest.TestCase):
    """Please note that the tests in this suite only works if a Redis
    host is available (see REDIS_HOST above).
    """
    def test_redis_connection(self):
        """Test that the Battleship server can correctly find a Redis
        instance.
        """
        with app.server.Battleship(REDIS_HOST, db=1) as battleship:
            self.assertTrue(battleship.ping_redis())

    def test_redis_add_open_game(self):
        """Test that the Battleship server can add an open game to the
        Redis instance.
        """
        with app.server.Battleship(REDIS_HOST, db=1) as battleship:
            con = battleship.redis_conn
            con.flushdb()

            result = con.get(battleship.OpenGames)
            self.assertIsNone(result)

            game = app.game.Game('New game!')
            result = battleship.add_open_game(game)
            self.assertTrue(result)

            results = con.lrange(battleship.OpenGames, 0, -1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].decode('utf-8'), game.id)

            result = battleship.close_open_game(game)
            self.assertTrue(result)

            results = con.lrange(battleship.OpenGames, 0, -1)
            self.assertEqual(len(results), 0)
