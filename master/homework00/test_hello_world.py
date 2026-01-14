import unittest

import homework00.hello_world as hello_world


class HelloTestCase(unittest.TestCase):
    def test_hello(self):
        m = "message"
        self.assertEqual(m, hello_world.text())
