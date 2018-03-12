"""
Unittest file for the Rat_Board module.
"""
from unittest import TestCase
from uuid import uuid4

from Modules.Rat_Board import RatBoard
from Modules.rat_rescue import Rescue


class RatBoardTests(TestCase):
    """
    Tests for RatBoard
    """

    def setUp(self):
        """
        Set up for each test
        """
        super().setUp()
        self.board = RatBoard()
        self.some_rescue = Rescue(uuid4(), "unit_test[BOT]", "snafu", "unit_test", board_index=-42)

    def tearDown(self):
        """
        Tear down after each test
        """

    def test_rescue_creation_existing_good_index(self):
        """
        verifies a rescue can be found
        """
        # spawn a new rescue with a ID
        self.board.create(rescue=self.some_rescue)
        self.assertEqual(self.board._rescues[-42], self.some_rescue)
