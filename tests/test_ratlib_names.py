import unittest

from ratlib.names import strip_name


class NamesTests(unittest.TestCase):
    def test_strip_name(self):
        """
        Verifies `ratlib.names.strip_name` correctly strips nicknames

        Returns:

        """
        raw_names = ['UNIT_TEST[BOT]', 'firehawk2421', 'xBoxRulz1911[xb|nd]']
        expected = ["UNIT_TEST", 'firehawk2421', 'xBoxRulz1911']

        i = 0
        for name in raw_names:
            with self.subTest(name=name):
                self.assertEqual(expected[i], strip_name(name))
                i += 1
