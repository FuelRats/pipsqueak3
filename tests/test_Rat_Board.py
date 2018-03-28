"""
Unittest file for the Rat_Board module.
"""
from unittest import TestCase, expectedFailure
from uuid import uuid4

from Modules.Rat_Board import RatBoard, IndexNotFreeError
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

    def test_rescue_creation_existing_good_index(self):
        """
        verifies a rescue can be added to the board when it already has an index
        """
        # spawn a new rescue with a ID
        self.board.append(rescue=self.some_rescue)
        self.assertEqual(self.board._rescues[-42], self.some_rescue)

    def test_def_rescue_creation_existing_bad_index(self):
        """
        Verifies a rescue cannot be added when its defined index is already in use.
        """
        # add it once
        self.board.append(rescue=self.some_rescue)
        # and try to add it again
        with self.assertRaises(IndexNotFreeError):
            self.board.append(rescue=self.some_rescue)

    def test_rescue_creation_with_overwrite(self):
        """
        Verifies a rescue can be added as to overwrite an existing entry.
        """
        self.board.append(rescue=self.some_rescue)
        my_rescue = Rescue(uuid4(), "foo", "bar", "foo", board_index=-42)
        self.board.append(rescue=my_rescue, overwrite=True)
        self.assertEqual(self.board._rescues[-42], my_rescue)

    def test_find_by_client_name(self):
        """
        Verifies an existing rescue can be found via `RescueBoard.find_by_name`
        """
        self.board.append(self.some_rescue)
        with self.subTest(condition="existing"):
            found = self.board.find_by_name(self.some_rescue.client)
            self.assertIsNotNone(found)

        with self.subTest(condition="not found"):
            found = self.board.find_by_name("foobar")
            self.assertIsNone(found)

    def test_find_by_case_number(self):
        """
        Verifies an existing rescue can be found via `RescueBoard.find_by_index`
        """
        self.board.append(self.some_rescue)
        with self.subTest(condition="existing"):
            found = self.board.find_by_index(self.some_rescue.board_index)
            self.assertIsNotNone(found)

        with self.subTest(condition="not found"):
            found = self.board.find_by_index(9001)
            self.assertIsNone(found)

    def test_find_by_uuid_offline(self):
        """
        Verifies an existing rescue can be found by uuid, without consulting the API
        """
        self.board.append(self.some_rescue)
        with self.subTest(condition="existing"):
            found = self.board.find_by_uuid(self.some_rescue.case_id)
            self.assertIsNotNone(found)

        with self.subTest(condition="not found"):
            found = self.board.find_by_uuid(uuid4())
            self.assertIsNone(found)

    def test_clear_board(self) -> None:
        """
        Verifies `RatBoard.clearBoard` functions as expected.
        """
        # make sure we have something on the board
        self.board.append(self.some_rescue)

        self.assertNotEqual(self.board._rescues, {})
        # if it is this test will prove nothing

        self.board.clear_board()

        self.assertEqual(self.board._rescues, {})

    def test_remove(self):
        """
        Verfies `RatBoard.remove()` correctly removes cases.
        """
        with self.subTest(conditon="existing"):
            # add the case
            self.board.append(self.some_rescue)
            self.assertNotEqual(self.board._rescues, {})
            self.board.remove(self.some_rescue)
            self.assertEqual(self.board._rescues, {})

        with self.subTest(condition="not existing"):
            with self.assertRaises(KeyError):
                self.board.remove(self.some_rescue)

    def test_contains_existing_by_uuid(self):
        """
        Verifies `RatBoard.__contains__` returns true when the a case with the same api UUID
        is known and tracked by the board

        Notes:
            This branch should only verify a rescue exists *with the same uuid*,
            it should do no further checks.
        """
        # add a case
        self.board.append(self.some_rescue)
        # make our assertion
        self.assertTrue(
            # spawn a case with the same uuid, and make our check
            Rescue(self.some_rescue.case_id, "nope", "i have no idea!", "nope") in self.board)

    @expectedFailure
    def test_contains_by_key_attributes(self):
        """
        Verifies `RatBoard.__contains__` returns true when a case with matching **key attributes**
        is known and tracked by the board.

        Notes:
            This branch checks for key attributes, even if the UUIDs don't match.
            This is necessary as cases do not have a UUID when created locally, and Mecha
            needs to be able to differentiate when an API created rescue is already on its board.

        See Also:
            `RatBoard.__contains__` documentation
        """
        guid = uuid4()
        name = self.some_rescue.client
        createdAt = self.some_rescue.created_at
        system = "Alpha Centuri".upper()
        my_rescue = Rescue(guid, client=name,
                           irc_nickname=name,
                           created_at=createdAt,
                           system=system)
        # this won't work yet because it depends on RatBoard.append to assign cases indexies.
        self.board.append(my_rescue)

        self.assertTrue(my_rescue in self.board)

    def test_contains_non_existing(self):
        """
        Verifies `Ratboard.__contains__` returns false when the desired rescue does not exist
            on the given board
        """
        self.assertFalse(self.some_rescue in self.board)

    def test_next_free_index(self):
        """Verifies RatBoard.<name> returns the first index that is not currently in use"""
        # check if no cases are on the board, the first index is zero
        self.assertEqual(self.board.next_free_index(), 0)

        my_rescue = self.some_rescue
        my_rescue.board_index = 0
        self.board.append(my_rescue)

        my_other_rescue = Rescue(uuid4(), "foo", "BAR", "halp", board_index=1)
        # my_other_rescue.board_index = 1

        self.board.append(my_other_rescue, overwrite=True)

        self.assertEqual(self.board.next_free_index(), 2)
