import grpc
import logging
import queue
import threading
import uuid
from battleships_pb2 import Attack, Request, Response, Status
from battleships_pb2_grpc import BattleshipsStub
from client_interface import ClientInterface


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BattleshipClient(ClientInterface):
    # The gRPC turn types mapped onto handler method names
    RESPONSES = {
        Response.State.BEGIN: 'begin',
        Response.State.START_TURN: 'start_turn',
        Response.State.STOP_TURN: 'end_turn',
        Response.State.WIN: 'win',
        Response.State.LOSE: 'lose',
    }

    # The gRPC report states mapped onto handler method names
    STATES = {
        Status.State.MISS: 'miss',
        Status.State.HIT: 'hit',
    }

    __supported_events = [
        'begin', 'start_turn', 'end_turn', 'attack',
        'hit', 'miss', 'win', 'lose'
    ]

    def __init__(self, grpc_host='localhost', grpc_port='50051'):
        self.__handlers = {}

        self.__host = grpc_host
        self.__port = grpc_port

        self.__player_id = ''
        self.__queue = queue.Queue()

        self.__channel = None
        self.__response_thread = None

    def __del__(self):
        if self.__channel is not None:
            self.__channel.close()

    def on(self, event=None):
        """A decorator that is used to register an event handler for a
        given event. This does the same as :meth:`add_event_handler`
        but is intended for decorator usage:

        @client.on(event='attack')
        def on_attack(vector):
            pass

        :param event: The event that the handler should listen for. If
                      this parameter is None, the event is inferred from
                      the handler's name. For instance, to add a handler
                      for `attack` messages, you can simply write:

                      @client.on()
                      def attack(vector):
                          pass

        Handlers that are supported are `begin`, `start_turn`,
        `end_turn`, `attack`, `hit`, `miss`, `defeat`.
        """

        def decorator(f):
            self.add_event_listener(event, f)
            return f

        return decorator

    def add_event_listener(self, event=None, handler=None):
        """Method that is used to register an event handler for a
        given event. See :meth:`on` for a detailed explanation.

        :param event: Event to register handler for
        :param handler: Handler for event
        """
        if event is None:
            event = handler.__name__

        if event not in self.__supported_events:
            raise ValueError(f'Unable to register event {event}!')

        logger.info(f'Registering {handler.__name__} for event "{event}"')

        self.__handlers[event] = handler

    def join(self):
        """This method sets up the client for sending and receiving gRPC
        messages to the server. It then sends a join message to the game
        server to indicate we are ready to play a new game.
        """
        self.__player_id = str(uuid.uuid4())

        logger.info(f'New player: {self.__player_id}')

        self.__channel = grpc.insecure_channel(f'{self.__host}:{self.__port}')

        stub = BattleshipsStub(self.__channel)
        responses = stub.Game(self.__stream())
        self.__response_thread = threading.Thread(
            target=lambda: self.__receive_responses(responses))
        self.__response_thread.daemon = True
        self.__response_thread.start()

        # Everything's set up, so we can now join a game
        self.__send(Request(join=Request.Player(id=self.__player_id)))

    def __send(self, msg):
        """Convience method that places a message in the queue for
        transmission to the game server.
        """
        self.__queue.put(msg)

    def attack(self, vector):
        """This method sends an Attack message with the associated vector
        to the game server. This method does not do any validation on the
        provided vector, other than that is must be a string. It is up to
        the caller to determine what the vector should look like.

        :param vector: Vector to send to game server, e.g., "G4"
        :raise ValueError: if vector is None or not a string
        """
        if vector is None or type(vector) is not str:
            raise ValueError('Parameter vector must be a string!')

        self.__send(Request(move=Attack(vector=vector)))

    def hit(self):
        """This method indicates to the game server that the received
        attack was a HIT. Oh no!
        """
        self.__send(Request(report=Status(state=Status.State.HIT)))

    def miss(self):
        """This method indicates to the game server that the received
        attack was a MISS. Phew!
        """
        self.__send(Request(report=Status(state=Status.State.MISS)))

    def defeat(self):
        """This method indicates to the game serve that the received
        attack was a HIT, which sunk the last of the remaining ships.
        In other words: Game Over. Too bad.
        """
        self.__send(Request(report=Status(state=Status.State.DEFEAT)))

    def __stream(self):
        """Return a generator of outgoing gRPC messages.

        :return: a gRPC message generator
        """
        while True:
            s = self.__queue.get()
            if s is not None:
                logger.info(f'{self.__player_id} - Sending {s}')
                yield s
            else:
                return

    def __receive_responses(self, in_stream):
        """Receive response from the gRPC in-channel.

        :param in_stream: input channel to handle
        """
        while True:
            try:
                response = next(in_stream)

                logger.info(f'{self.__player_id} - Received {response}')

                self.__handle_response(response)
            except StopIteration:
                return

    def __handle_response(self, msg):
        """This method handles the actual response coming from the game
        server.

        :param msg: Message received from the game server
        """
        which = msg.WhichOneof('event')
        if which == 'turn':
            if msg.turn in self.RESPONSES:
                self.__exc_callback(self.RESPONSES[msg.turn])
            else:
                logger.error('Response contains unknown state!')

        elif which == 'move':
            self.__exc_callback('attack', msg.move.vector)

        elif which == 'report':
            if msg.report.state in self.STATES:
                self.__exc_callback(self.STATES[msg.report.state])
            else:
                logger.error('Report contains unknown state!')

        else:
            logger.error('Got unknown response type!')

    def __exc_callback(self, *args):
        """Convenience method that calls the appropriate callback
        function if it has been registered.
        """
        cmd = args[0]
        if cmd in self.__handlers:
            args = args[1:]
            if not args:
                self.__handlers[cmd]()
            else:
                self.__handlers[cmd](*args)
