class Battleship:
    __allowed_events = [
        'begin', 'start_turn', 'end_turn', 'attack', 'hit', 'miss', 'defeat'
    ]

    def __init__(self):
        self.handlers = {}

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

        Handlers that are supported are `attack`, `report`, `hit`,
        `miss`, `defeat`, `start_turn`, `stop_turn`.
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

        if event not in self.__allowed_events:
            raise ValueError(f'Unable to register event {event}!')

        print(f'Registering {handler.__name__} for event "{event}"')
        self.handlers[event] = handler

    def attack(self, vector):
        """This method sends an Attack message with the associated vector
        to the game server. This method does not do any validation on the
        provided vector, other than that is must be a string. It is up to
        the caller to determine what the vector should look like.

        :param vector: Vector to send to game server, e.g., "G4"
        """
        if vector is None or type(vector) is not str:
            raise ValueError('Parameter vector must be a string!')

    def hit(self):
        """This method indicates to the game server that the received
        attack was a HIT. Oh no!
        """
        pass

    def miss(self):
        """This method indicates to the game server that the received
        attack was a MISS. Phew!
        """
        pass

    def defeat(self):
        """This method indicates to the game serve that the received
        attack was a HIT, which sunk the last of the remaining ships.
        In other words: Game Over. Too bad.
        """
        pass
