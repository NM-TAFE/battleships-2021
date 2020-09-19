import grpc
import log
import os
from battleships_pb2_grpc import add_BattleshipsServicer_to_server
from concurrent.futures import ThreadPoolExecutor
from server import Battleship

logger = log.get_logger(__name__)


def main():
    serve_port = os.getenv('PORT', '50051')
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')

    battleship = Battleship(redis_host, redis_port)
    if not battleship.ping_redis():
        logger.fatal('Unable to connect to a Redis instance '
                     f'{redis_host}:{redis_port}')
        exit(1)

    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    add_BattleshipsServicer_to_server(battleship, server)

    server.add_insecure_port(f'[::]:{serve_port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()
