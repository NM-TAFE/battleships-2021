import log
from threading import Lock

logger = log.get_logger(__name__)


class Game:
    def __init__(self, _id):
        self.__id = _id
        self.__my_turn = False
        self.__lock = Lock()

    @property
    def id(self):
        """Get the game's ID.

        :return: Game ID
        """
        return self.__id

    @property
    def my_turn(self):
        """Is it my turn?

        :return: True if it is my turn, False otherwise
        """
        with self.__lock:
            return self.__my_turn

    def start_turn(self):
        """Start turn for this player (as the Game server hosts a Game
        instance for a single player at a time).
        """
        with self.__lock:
            self.__my_turn = True

    def end_turn(self):
        """End turn for this player (as the Game server hosts a Game
        instance for a single player at a time).
        """
        with self.__lock:
            self.__my_turn = False
