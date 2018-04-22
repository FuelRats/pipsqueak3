"""
Unittest file for the Rat_Board module.
"""
from copy import deepcopy
from unittest import TestCase
from uuid import uuid4

import pytest

from Modules.rat_board import RatBoard, IndexNotFreeError, RescueNotChangedException
from Modules.rat_rescue import Rescue
from ratlib.names import Platforms


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
        self.assertEqual(self.board.rescues[-42], self.some_rescue)

    def test_rescue_creation_existing_bad_index(self):
        """
        Verifies a rescue cannot be added when its defined index is already in use.
        """
        # add it once
        self.board.append(rescue=self.some_rescue)
        # and try to add it again
        with self.assertRaises(IndexNotFreeError):
            self.board.append(rescue=self.some_rescue)

    def test_rescue_Creation_without_index(self):
        """
        Verifies a Rescue can be added without a defined index.
            the board should give our rescue one.
        """
        guid = uuid4()
        name = "SicklyTadPole"
        my_rescue = Rescue(guid, name, "NLTT 48288", name)

        self.board.append(my_rescue)

        found = self.board.find_by_uuid(guid)
        self.assertIsNotNone(found)
        self.assertEqual(found.client, name)

    def test_rescue_creation_with_overwrite(self):
        """
        Verifies a rescue can be added as to overwrite an existing entry.
        """
        self.board.append(rescue=self.some_rescue)
        my_rescue = Rescue(uuid4(), "foo", "bar", "foo", board_index=-42)
        self.board.append(rescue=my_rescue, overwrite=True)
        self.assertEqual(self.board.rescues[-42], my_rescue)

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

        self.assertNotEqual(self.board.rescues, {})
        # if it is this test will prove nothing

        self.board.clear_board()

        self.assertEqual(self.board.rescues, {})

    # moved to PyTest module
    # def test_remove(self):
    #     """
    #     Verfies `RatBoard.remove()` correctly removes cases.
    #     """
    #     with self.subTest(conditon="existing"):
    #         # add the case
    #         self.board.append(self.some_rescue)
    #         self.assertNotEqual(self.board.rescues, {})
    #         self.board.remove(self.some_rescue)
    #         self.assertEqual(self.board.rescues, {})
    #
    #     with self.subTest(condition="not existing"):
    #         with self.assertRaises(KeyError):
    #             self.board.remove(self.some_rescue)

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


    def test_contains_non_existing(self):
        """
        Verifies `Ratboard.__contains__` returns false when the desired rescue does not exist
            on the given board
        """
        self.assertFalse(self.some_rescue in self.board)



class TestRatBoardPyTest(object):
    """
    Container for pyTest style tests for the RatBoard
    """
    @pytest.mark.asyncio
    async def test_remove(self, RescueSoP_fx: Rescue, RatBoard_fx: RatBoard):
        # append a rescue to the board
        RatBoard_fx.rescues[RescueSoP_fx.board_index] = RescueSoP_fx
        # and attempt to remove it
        await RatBoard_fx.remove(rescue=RescueSoP_fx)

        assert RescueSoP_fx.board_index not in RatBoard_fx.rescues

    @pytest.mark.asyncio
    async def test_modify_with_net_change(self, RescueSoP_fx: Rescue, RatBoard_fx: RatBoard):
        # make a deep copy of the fixture so we can edit it without tainting the board reference
        myRescue: Rescue = deepcopy(RescueSoP_fx)
        # append our rescue to the board
        RatBoard_fx.rescues[RescueSoP_fx.board_index] = RescueSoP_fx

        # make a change, ensure a change actually occured.
        myRescue.platform = Platforms.PC if myRescue.platform is not Platforms.PC else Platforms.XB
        result = await RatBoard_fx.modify(rescue=myRescue)
        # check status OK
        assert result is True
        # check that a change occured
        assert RatBoard_fx.rescues[RescueSoP_fx.board_index] == myRescue

        # double check
        assert RatBoard_fx.rescues[RescueSoP_fx.board_index] != RescueSoP_fx

    @pytest.mark.asyncio
    async def test_modify_no_net_change(self, RescueSoP_fx: Rescue, RatBoard_fx: RatBoard):
        # append rescue to board
        RatBoard_fx.rescues[RescueSoP_fx.board_index] = RescueSoP_fx

        with pytest.raises(RescueNotChangedException):
            await RatBoard_fx.modify(rescue=RescueSoP_fx)


    def test_contains_by_key_attributes(self, RescueSoP_fx: Rescue, RatBoard_fx: RatBoard):
        """
        Verifies `Ratboard.__contains__` returns true when looking for a case by
            key attributes only

        Args:
            RescueSoP_fx (Rescue): rescue fixture
            RatBoard_fx (RatBoard): RatBoard fixture
        """
        # add our rescue to the board
        RatBoard_fx.append(rescue=RescueSoP_fx)

        # overwrite our local rescue objects id
        RescueSoP_fx._id = None

        assert RescueSoP_fx in RatBoard_fx

    @pytest.mark.parametrize("garbage", [None, 42, -2.2, uuid4(), []])
    def test_rescue_setter_garbage(self, RatBoard_fx: RatBoard, garbage):
        """
        Tests Ratboard.rescue
        Args:
            RatBoard_fx (RatBoard):  Ratboard fixture
            garbage (): Garbage to throw at property
        """
        with pytest.raises(TypeError):
            RatBoard_fx.rescues = garbage


    @pytest.mark.parametrize("index", [i for i in range(0, 5)])
    def test_next_free_index_free(self, index: int, RatBoard_fx: RatBoard):
        """Verifies ratboard.next_free_index returns a free index when there are free available"""

        # make a copy of the fixture, so we don't taint other tests (this is preemptive)
        myBoard = deepcopy(RatBoard_fx)
        # myBoard.regen_index()

        # write the key
        myBoard.rescues[index] = None

        # and the previous keys
        keys = range(0, index)
        for i in keys:
            myBoard.rescues[i] = None

        nextFree = myBoard.next_free_index()

        assert index + 1 == nextFree

    @pytest.mark.parametrize("keys,expected",( ([0, 1, 2, 4], 3), ([0, 2, 3], 1)))
    def test_next_free_mixed_board(self, keys: list, expected: int, RatBoard_fx: RatBoard):
        #local duplicate of the fixture
        myBoard = deepcopy(RatBoard_fx)

        # populate rescues dict
        for i in keys:
            myBoard.rescues[i] = None

        # roll the tested method
        nextFree = myBoard.next_free_index()

        # and verify its functionality
        assert expected == nextFree