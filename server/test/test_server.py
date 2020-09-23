import unittest
from game import Game
import server

REDIS_HOST = '192.168.20.50'


class TestServer(unittest.TestCase):
    """Please note that the tests in this suite only work if a Redis
    host is available (see REDIS_HOST above).
    """
    def test_redis_connection(self):
        """Test that the Battleship server can correctly find a Redis
        instance.
        """
        with server.Battleship(REDIS_HOST, db=1) as battleship:
            self.assertTrue(battleship.ping_redis())

    def test_redis_add_open_game(self):
        """Test that the Battleship server can add an open game to the
        Redis instance.
        """
        with server.Battleship(REDIS_HOST, db=1) as battleship:
            con = battleship.redis_conn
            con.flushdb()

            result = con.get(battleship.OpenGames)
            self.assertIsNone(result)

            game = Game('New game!')
            result = battleship.add_open_game(game)
            self.assertTrue(result)

            results = con.lrange(battleship.OpenGames, 0, -1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].decode('utf-8'), game.id)

            result = battleship.close_open_game(game)
            self.assertTrue(result)

            results = con.lrange(battleship.OpenGames, 0, -1)
            self.assertEqual(len(results), 0)

    def test_find_game(self):
        """Test that the Battleship server can create a new game if no
        open game is found and that it can find an open game in Redis
        if one is actually there.
        """
        with server.Battleship(REDIS_HOST, db=1) as battleship:
            con = battleship.redis_conn
            con.flushdb()

            game, is_new = battleship.find_game_or_create()
            self.assertTrue(is_new)

            game = Game('new game')
            result = battleship.add_open_game(game)
            self.assertTrue(result)

            found_game, is_new = battleship.find_game_or_create()
            self.assertFalse(is_new)
            self.assertEqual(game.id, found_game.id)
