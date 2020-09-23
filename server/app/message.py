import json
from dataclasses import dataclass


@dataclass
class Message:
    """This class describes the message objects that are passed through
    Redis using PubSub.

    The messages are used to communicate between two Game servers which
    are in fact playing the same game. Please note that no validation
    takes place as to whether the provided {type} is valid even though
    message types (BEGIN, etc.) are provided for convenience.
    """
    type: str
    player: str
    data: str

    # Messages types (no validation is performed)
    BEGIN = 'begin'
    STOP_TURN = 'stop_turn'
    ATTACK = 'attack'
    STATUS = 'status'
    LOST = 'lost'

    def dumps(self):
        """Create a JSON object that can be used to send the message
        to a Redis instance.

        :return: JSON encoded string
        """
        return json.dumps({
            'type': self.type,
            'player': self.player,
            'data': self.data,
        })

    @staticmethod
    def recreate(s):
        """Recreate Message object from serialized string as it might
        be received from a Redis instance.

        :param s: the JSON encoded string
        :return: Message object as recreated from the JSON string
        :raise ValueError: if the JSON string cannot be parsed
        """
        d = json.loads(s)
        if 'type' not in d or 'player' not in d or 'data' not in d:
            raise ValueError()

        return Message(d['type'], d['player'], d['data'])
