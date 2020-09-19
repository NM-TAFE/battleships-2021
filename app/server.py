import backoff
import redis
import uuid
import log
import battleships_pb2_grpc
from game import Game

logger = log.get_logger(__name__)


class Battleship(battleships_pb2_grpc.BattleshipsServicer):
    OpenGames = 'openGames'

    def __init__(self, redis_host, redis_port='6379', db=0):
        """Create a Battleship (server) instance.

        :param redis_host: Hostname of Redis instance
        :param redis_port: Port of Redis instance
        :param db: Database to use within Redis instance
        """
        self.__r = redis.Redis(host=redis_host, port=redis_port, db=db)

    def __enter__(self):
        """Entry point for the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit point for the context manager.

        Closes any open connections.
        """
        self.close()

    def Game(self, request_iterator, context):
        """This method is the implementation of the gRPC Game service.
        When connected, this provides the main functionality of the
        Battleship game.
        """
        request = next(request_iterator)
        player_id = request.join.id
        if player_id == '':
            logger.error('Player message does not contain valid ID')
            return

        logger.info(f'Player {player_id} is attempting to join')

        game, is_new = self.find_game()

        logger.info(f'Connecting to game {game.id}. '
                    f'New? {"Yes" if is_new else "No"}')
        logger.info('Setting up server to start receiving PubSub messages')

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError)
    def __ping_redis(self):
        """Ping Redis instance to see if it's alive.

        This method may raise the ConnectionError exception if it can't
        connect to a Redis instance.

        :return: True if Redis instance reachable, raises ConnectionError
        otherwise
        """
        return self.__r.ping()

    def ping_redis(self):
        """Ping a Redis instance.

        :return: True if connection to instance established, False otherwise
        """
        try:
            return self.__ping_redis()
        except redis.exceptions.ConnectionError:
            return False

    @property
    def redis_conn(self):
        """Return Redis client as a property.
        """
        return self.__r

    def close(self):
        """Close the connection the Redis instance.
        """
        self.__r.close()

    def connect_game(self, game, player, is_new):
        """Join an existing game or advertise this one as open if game
        is not yet in progress.

        :param game: Game
        :param player: Player
        :param is_new: True if game is new, False otherwise
        """
        pass

    def find_game(self):
        """Try to find an open game in Redis or create a new game if
        none found.

        :return: A tuple containing a Game object and a flag is_new
        which indicates that a new game was created.
        """
        b_game_id = self.__r.rpop(self.OpenGames)

        # b_game_id is None if no open game found
        is_new = b_game_id is None
        if is_new:
            logger.info('Could not find open game, creating new one')
            game_id = str(uuid.uuid4())
        else:
            game_id = b_game_id.decode('utf-8')

        return Game(game_id), is_new

    def add_open_game(self, game):
        """Add an open game to the Redis instance so it can be discovered.

        :param game: Game to be advertised
        """
        logger.info(f'Adding open game {game.id}')
        return self.__r.lpush(self.OpenGames, game.id)

    def close_open_game(self, game):
        """Remove an open game from the Redis instance so it can no longer
        be discovered.

        :param game: Game to be closed
        """
        logger.info(f'Closing open game {game.id}')
        return self.__r.lrem(self.OpenGames, 1, game.id)
