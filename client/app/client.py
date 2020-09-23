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
