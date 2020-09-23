import unittest
from game import Game


class TestGame(unittest.TestCase):
    def test_game(self):
        """Test some of the properties of a Game.
        """
        game_id = 'Some new game'
        game = Game(game_id)
        self.assertEqual(game.id, game_id)
        self.assertFalse(game.my_turn)

        game.start_turn()
        self.assertTrue(game.my_turn)

        game.end_turn()
        self.assertFalse(game.my_turn)
