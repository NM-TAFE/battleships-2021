import unittest
from message import Message


class TestMessage(unittest.TestCase):
    def setUp(self) -> None:
        self.type = Message.BEGIN
        self.player = "Player McPlayerface"
        self.data = "Some data"
        self.msg = Message(self.type, self.player, self.data)

    def test_create_message(self):
        self.assertEqual(self.msg.type, self.type)
        self.assertEqual(self.msg.player, self.player)
        self.assertEqual(self.msg.data, self.data)

    def test_json_encode_message(self):
        j = self.msg.dumps()
        self.assertEqual(j, '{"type": "begin", "player": "Player McPlayerface"'
                            ', "data": "Some data"}')

    def test_decode_json_encoded_message(self):
        x = Message.recreate(self.msg.dumps())

        # We check that the original message and the recreated one are equal
        self.assertEqual(self.msg, x)

        # We check that the recreated message is not the same instance as
        # the original message
        self.assertIsNot(self.msg, x)
