import json
from dataclasses import dataclass


@dataclass
class Message:
    """This class describes the message objects that are passed through
    Redis using PubSub.

    The messages are used to communicate between two Game servers which
    are in fact playing the same game.
    """
    typ: str
    player: str
    data: str

    BEGIN = 'begin'
    STOP_TURN = 'stop_turn'
    STATUS = 'status'
    LOST = 'lost'

    def dumps(self):
        """Create a JSON object that can be used to send the message
        to a Redis instance.

        :return: JSON encoded string
        """
        return json.dumps({
            'typ': self.typ,
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
        if 'typ' not in d or 'player' not in d or 'data' not in d:
            raise ValueError()

        return Message(d['typ'], d['player'], d['data'])
