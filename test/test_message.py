import unittest
from app.message import Message


class TestMessage(unittest.TestCase):
    def setUp(self) -> None:
        self.typ = Message.BEGIN
        self.player = "Player McPlayerface"
        self.data = "Some data"

    def test_create_message(self):
        m = Message(self.typ, self.player, self.data)
        self.assertEqual(m.typ, self.typ)
        self.assertEqual(m.player, self.player)
        self.assertEqual(m.data, self.data)

    def test_json_encode_message(self):
        m = Message(self.typ, self.player, self.data)
        j = m.dumps()
        self.assertEqual(j, '{"typ": "begin", "player": "Player McPlayerface"'
                            ', "data": "Some data"}')

    def test_decode_json_encoded_message(self):
        m = Message(self.typ, self.player, self.data)
        j = m.dumps()
        x = Message.recreate(j)
        self.assertEqual(m, x)
