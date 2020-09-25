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

    try:
        battleship = Battleship(redis_host, redis_port)
        server = grpc.server(ThreadPoolExecutor(max_workers=10))
        add_BattleshipsServicer_to_server(battleship, server)

        logger.info(f'Starting server on port {serve_port}')

        server.add_insecure_port(f'[::]:{serve_port}')
        server.start()
        server.wait_for_termination()
    except ConnectionError:
        logger.fatal('Unable to reach Redis server!')
        exit(1)


if __name__ == '__main__':
    main()
