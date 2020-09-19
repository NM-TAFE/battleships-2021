import backoff
import redis
import log
import battleships_pb2_grpc

logger = log.get_logger(__name__)


class Battleship(battleships_pb2_grpc.BattleshipsServicer):
    def __init__(self, redis_host, redis_port):
        """Create a Battleship (server) instance.

        :param redis_host: Hostname of Redis instance
        :param redis_port: Port of Redis instance
        """
        self.__r = redis.Redis(host=redis_host, port=redis_port)

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
    def redis(self):
        """Return Redis client as a property.
        """
        return self.__r

    def close(self):
        """Close the connection the Redis instance.
        """
        self.__r.close()
