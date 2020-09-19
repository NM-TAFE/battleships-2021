import log
from threading import Lock

logger = log.get_logger(__name__)


class Game:
    def __init__(self, id=None):
        self.__id = id
        self.__my_turn = False
        self.__lock = Lock()

    @property
    def id(self):
        return self.__id

    @property
    def my_turn(self):
        return self.__my_turn
