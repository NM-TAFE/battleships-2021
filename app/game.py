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
        """Game ID.

        :return: Game ID
        """
        return self.__id

    @property
    def my_turn(self):
        """Is it my turn?

        :return: True if it is my turn, False otherwise
        """
        return self.__my_turn
