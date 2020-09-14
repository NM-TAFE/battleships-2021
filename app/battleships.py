import grpc
from concurrent.futures import ThreadPoolExecutor
import battleships_pb2_grpc


class BattleshipsServicer(battleships_pb2_grpc.BattleshipsServicer):
    def Game(self, request_iterator, context):
        for request in request_iterator:
            pass


def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    battleships_pb2_grpc.add_BattleshipsServicer_to_server(
        BattleshipsServicer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
