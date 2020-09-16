import grpc
from concurrent.futures import ThreadPoolExecutor
from battleships_pb2_grpc import BattleshipsServicer, add_BattleshipsServicer_to_server


class BattleshipsServer(BattleshipsServicer):
    def Game(self, request_iterator, context):
        for request in request_iterator:
            pass


def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    add_BattleshipsServicer_to_server(BattleshipsServer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
