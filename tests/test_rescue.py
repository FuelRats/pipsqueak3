"""
test_rescue.py - tests for Rescue and RescueBoard objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from copy import deepcopy
from datetime import datetime
from typing import List
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest

from Modules.context import Context
from Modules.rat_rescue import Rescue
from Modules.rats import Rats
from Modules.user import User
from utils.ratlib import Platforms


class TestRescue(TestCase):
    """
    Tests for `Modules.Rescue.Rescue`
    """

    def setUp(self):
        self.time = datetime(2017, 12, 24, 23, 59, 49)
        self.updated_at = datetime(2017, 12, 24, 23, 59, 52)
        self.system = "firestone"
        self.case_id = "some_id"
        self.rescue = Rescue(self.case_id, "stranded_commander", system=self.system, irc_nickname="stranded_commander",
                             created_at=self.time, updated_at=self.updated_at, board_index=42)

    def test_client_property_exists(self):
        """
        Verifies the `Rescue.client` property exists\n
        :return:
        :rtype:
        """
        self.assertTrue(hasattr(self.rescue, "client"))
        self.assertEqual(self.rescue.client, "stranded_commander")

    def test_client_writeable(self):
        """
        Verifies the `Rescue.client` property can be written to correctly\n
        :return:
        :rtype:
        """
        expected = "some other commander"
        self.rescue.client = expected
        self.assertEqual(self.rescue.client, expected)

    def test_created_at_made_correctly(self):
        """
        Verifies the `Rescue.created_at` property was correctly created\n
        :return:
        :rtype:
        """
        self.assertEqual(self.time, self.rescue.created_at)

    def test_created_at_not_writable(self):
        """
        Verifies the `Rescue.created_at` property cannot be written to\n
        :return:
        :rtype:
        """
        with self.assertRaises(AttributeError):
            self.rescue.created_at = datetime.utcnow()

    def test_updated_at_initial(self):
        """
        Verify `Rescue.updated_at` was initialized correctly.

        Returns:

        """
        self.assertEqual(self.updated_at, self.rescue.updated_at)

    def test_updated_at_settable_correctly(self):
        """
        Verifies `Rescue.updated_at` can be set properly

        Returns:

        """
        my_time = datetime.now()
        self.rescue.updated_at = my_time
        self.assertEqual(my_time, self.rescue.updated_at)

    def test_updated_at_value_error(self):
        """
        Verifies `Rescue.updated_at` returns a `ValueError` if a bad date is
         given.

        Returns:

        """
        with self.assertRaises(ValueError):
            self.rescue.updated_at = datetime(2012, 1, 1, 1, 1, 1)

    def test_updated_at_type_error(self):
        """
        Verifies `Rescue.updated_at` raises a `TypeError` when someone throws
        garbage at it

        Returns:

        """
        garbage = [12, "foo", [], {}, False, None]
        for value in garbage:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.rescue.updated_at = value

    def test_system_initial_set(self):
        """
        Verifies the `Rescue.system` property was correctly set during init\n
        :return:
        :rtype:
        """
        self.assertEqual(self.system.upper(), self.rescue.system)

    def test_system_writable(self):
        self.rescue.system = "sol"
        self.assertEqual(self.rescue.system, "SOL")

    def test_case_id(self):
        self.assertEqual(self.case_id, self.rescue.case_id)

    def test_get_active(self):
        """
        Verifies `Rescue.active` is readable and set correctly by default
        :return:
        :rtype:
        """
        self.assertTrue(self.rescue.active)

    def test_set_active_correctly(self):
        """
        Tests the `Rescue.active` property for expected function
        :return:
        :rtype:
        """
        states = [True, False]
        for state in states:
            with self.subTest(state=state):
                self.rescue.active = state

    def test_set_active_set_incorrectly(self):
        """
        Tests the `Rescue.active` property for the correct usage errors
        :return:
        :rtype:
        """
        with self.assertRaises(ValueError):
            self.rescue.active = "something totally not right"

    def test_get_quotes(self):
        """
        Verifies the default settings for `Rescue.quotes` property are set
        correctly And confirms the property is readable.\n
        :return:
        :rtype:
        """
        self.assertEqual([], self.rescue.quotes)

    def test_write_quotes_correctly(self):
        """
        Verifies the `Rescue.quotes` property can be written to when given a
        list

        :return:
        :rtype:
        """
        self.rescue.quotes = ["foo"]
        self.assertEqual(["foo"], self.rescue.quotes)

    def test_write_quotes_incorrectly(self):
        """
        Verifies `Rescue.quotes` cannot be set to wierd things that are not
         lists

        :return:
        :rtype:
        """
        names = [False, True, "string", {}, 12]
        for name in names:
            with self.assertRaises(ValueError):
                self.rescue.quotes = name

    def test_add_quote_with_name(self):
        # verify the list was empty
        self.assertEqual(self.rescue.quotes, [])
        # add ourselves a quote
        self.rescue.add_quote(message="foo", author='unit_test[BOT]')
        # verify something got written to the rescue property
        self.assertEqual(1, len(self.rescue.quotes))
        # now verify that something is what we wanted to write
        self.assertEqual("foo", self.rescue.quotes[0].message)
        self.assertEqual("unit_test[BOT]", self.rescue.quotes[0].author)

    def test_add_quote_mecha(self):
        # verify the list was empty
        self.assertEqual(self.rescue.quotes, [])
        # add ourselves a quote
        self.rescue.add_quote(message="foo")
        # verify something got written to the rescue property
        self.assertEqual(1, len(self.rescue.quotes))
        # now verify that something is what we wanted to write
        self.assertEqual("foo", self.rescue.quotes[0].message)
        self.assertEqual("Mecha", self.rescue.quotes[0].author)

    # @expectedFailure
    @patch('tests.test_rescue.Rescue.updated_at')
    def test_change_context_manager(self, mock_updated_at: MagicMock):
        """
        Verifies the `Rescue.change` context manager functions as expected.
        Currently that is simply to update the `Rescue.updated_at` is updated.
        Returns:

        """
        origin = self.rescue.updated_at
        with self.rescue.change():
            pass
        self.assertNotEqual(origin, self.rescue.updated_at)

    def test_get_board_index(self):
        """
        Verifies `Rescue.board_index` was set correctly during init.

        Returns:

        """
        self.assertEqual(42, self.rescue.board_index)

    def test_set_board_index_correctly(self):
        """
        Verifies `Rescue.board_index` is settable

        Returns:
        """
        self.rescue.board_index = 24
        self.assertEqual(24, self.rescue.board_index)

    def test_set_board_index_incorrectly(self):
        """
        verifies attempts to set `Rescue.board_index` to things other than
        ints, or below zero, Fail with the correct errors.
        Returns:

        """
        bad_values_type = ["foo", [], {}]
        bad_values_ints = [-42, -2]
        for value in bad_values_ints:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.rescue.board_index = value

        for value in bad_values_type:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.rescue.board_index = value

    def test_unidentified_rats_properly(self):
        """
        Verifies `Rescue.unidentified_rats` can be written to with good data

        Returns:

        """
        # verify it was empty to begin with (default)
        self.assertEqual(self.rescue.unidentified_rats, [])
        # lets make some names
        names = ["UNIT_TEST[BOT]", "flying_potato", "random_person"]
        # set the property
        self.rescue.unidentified_rats = names
        # verify the property.
        self.assertEqual(self.rescue.unidentified_rats, names)

    def test_unidentified_rats_bad_types(self):
        """
        Verifies the correct exception is raised when someone throws garbage
        at `Rescue.unidentified_rats`

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.unidentified_rats = piece

    def test_is_open_properly(self):
        """
        Verifies `Rescue.open` is readable and settable when thrown good
        parameters

        Returns:

        """
        # check default state
        self.assertTrue(self.rescue.open)

        data = [True, False]
        for value in data:
            with self.subTest(value=value):
                self.rescue.open = value
                self.assertEqual(self.rescue.open, value)

    def test_is_open_bad_types(self):
        """
        Verifies `Rescue.is_open` raises correct exceptions when its given
        garbage

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.open = piece

    def test_epic_readable(self):
        """
        Verifies  `Rescue.epic` is readable.

        Returns:

        """
        # check default state
        self.assertFalse(self.rescue.epic)

    def test_code_red_properly(self):
        """
        Verifies `Rescue.code_red` is readable and settable when thrown good
        parameters

        Returns:

        """
        # check default state
        self.assertFalse(self.rescue.code_red)

        data = [True, False]
        for value in data:
            with self.subTest(value=value):
                self.rescue.code_red = value
                self.assertEqual(self.rescue.code_red, value)

    def test_code_red_bad_types(self):
        """
        Verifies `Rescue.code_red` raises correct exceptions when its given
         garbage

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.code_red = piece

    def test_title(self):
        """
        Verifies `Rescue.title` behaves as expected
        """

        with self.subTest(condition="good"):
            if self.rescue.title:
                self.rescue.title = None
                self.assertIsNone(self.rescue.title)

            title = "foobar express"
            self.rescue.title = title
            self.assertEqual(self.rescue.title, title)

        with self.subTest(condition="garbage"):
            garbage = [[], {}, 42, 22., 0, uuid4()]
            for piece in garbage:
                with self.subTest(piece=piece):
                    with self.assertRaises(TypeError):
                        self.rescue.title = piece

    def test_rats_good_data(self):
        """
        Verfifies the `Rescue.rats` property behaves as expected
        """
        self.assertEqual(self.rescue.rats, [])
        data = [Rats(uuid4(), "unit_Test"), Rats(uuid4(), "icarus")]
        self.rescue.rats = data
        self.assertEqual(self.rescue.rats, data)

    def test_rats_bad_types(self):
        """
        Verifies the proper exception is raised when `Rescue.rats` is given garbage params
        """
        garbage = [{}, -1, 0, .2, (2, 3), uuid4()]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.rats = piece

    def test_eq_true_branch(self):
        """
        Verifies Rescue.__eq__ functions as expected when comparing two rescues
         - verifies the true branch
        """
        # is this total overkill?
        self.assertTrue(self.rescue == self.rescue)



    def test_eq_false_branch(self):
        """
        Verifies Rescue.__eq__ functions as expected when comparing two rescues
             - verifies the false branch
        """
        foo = Rescue(uuid4(), "snafu", "firestone", "snafu")
        self.assertFalse(self.rescue == foo)

    def test_platform_valid(self):
        """
        Verfiies Rescue.platform setter and getter function as expected when given valid data
        """
        platforms = [Platforms.PC, Platforms.PS, Platforms.XB, Platforms.DEFAULT]
        for platform in platforms:
            with self.subTest(platform=platform):
                self.rescue.platform = platform
                self.assertEqual(self.rescue.platform, platform)
                self.assertEqual(self.rescue._platform, self.rescue.platform)

    def test_platform_invalid(self):
        garbage = ["pc", None, 42, 12.2, []]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.platform = piece


class TestRescuePyTests(object):
    """
    container for pytest specific tests
    """

    @pytest.mark.asyncio
    async def test_add_rats_bad_id(self, rat_no_id_fx, rescue_sop_fx):
        """
        Verifies attempting to add a rat that does not have a API id fails as expected
        """
        with pytest.raises(ValueError, message="Assigned rat does not have a known API ID"):
            await rescue_sop_fx.add_rat(rat=rat_no_id_fx)

        assert rat_no_id_fx not in rescue_sop_fx.rats

    @pytest.mark.asyncio
    async def test_add_rats_ok(self, rat_good_fx, rescue_sop_fx):
        """
        Verifies adding a existing rat with a UUID works
        Args:
            rat_good_fx (Rats): Good Rat object Test Fixture
            rescue_sop_fx (Rescue):  Rescue object Test Fixture
        """
        # rescue_sop_fx:Rescue
        await rescue_sop_fx.add_rat(rat=rat_good_fx)
        assert rat_good_fx in rescue_sop_fx.rats

    @pytest.mark.asyncio
    async def test_add_rat_from_cache(self, rat_good_fx: Rats, rescue_sop_fx: Rescue):
        await rescue_sop_fx.add_rat(rat_good_fx.name)
        assert rat_good_fx == rescue_sop_fx.rats[0]

    @pytest.mark.parametrize("garbage", [(None,), (42,), (-2.2,), (uuid4(),)])
    def test_irc_nickname_garbage(self, garbage, rescue_plain_fx: Rescue):
        """
        Verifies throwing garbage types at Rescue.irc_nickname results in a TypeError
        Args:
            garbage (): Garbage to throw
            rescue_plain_fx (Rescue): Plain rescue Fixture
        """
        with pytest.raises(TypeError):
            rescue_plain_fx.irc_nickname = garbage

    @pytest.mark.parametrize("test_input", ["foo", "bar", "en-us", "RU-RU"])
    def test_irc_nickname_strings(self, test_input, rescue_plain_fx: Rescue):
        """
        Verifies the irc nickname can be set when passed a string

        Args:
            test_input (str): values to test
            rescue_plain_fx (Rescue): Rescue fixture

        """

        rescue_plain_fx.irc_nickname = test_input
        assert rescue_plain_fx.irc_nickname == test_input

    @pytest.mark.parametrize("garbage", [None, 42, -2.2, uuid4()])
    def test_lang_id_garbage(self, garbage, rescue_plain_fx: Rescue):
        """
        Verifies throwing garbage types at Rescue.lang_id results in a TypeError
        Args:
            garbage (): Garbage to throw
            rescue_plain_fx (Rescue): Plain rescue Fixture
        """
        with pytest.raises(TypeError):
            rescue_plain_fx.lang_id = garbage

    @pytest.mark.parametrize("test_input", ["foo", "bar", "en-us", "RU-RU"])
    def test_lang_id_strings(self, test_input, rescue_plain_fx: Rescue):
        """
        Verifies the lang id can be set when passed a string

        Args:
            test_input (str): values to test
            rescue_plain_fx (Rescue): Rescue fixture

        """

        rescue_plain_fx.lang_id = test_input
        assert rescue_plain_fx.lang_id == test_input

    def test_set_unidentified_rats_garbage_in_list(self, rescue_plain_fx: Rescue):
        """
        Verifies a ValueError is raised if the list passed to Rats.unidentified_Rats contains
            illegal values
        """
        garbage = [12, -42.2, None]
        with pytest.raises(ValueError):
            rescue_plain_fx.unidentified_rats = garbage

    @pytest.mark.parametrize("reason,reporter,marked", [
        ("some reason", "UNIT_TEST[BOT]", True),
        ("Totally not md", "Potato", False),
        (None, None, True),
        (None, None, False)
    ])
    def test_mark_for_deletion_setter_valid(self, rescue_sop_fx: Rescue, reason: str, reporter: str,
                                            marked: bool):
        rescue_sop_fx.mark_for_deletion.reporter = reporter
        assert rescue_sop_fx.mark_for_deletion.reporter == reporter

        rescue_sop_fx.mark_for_deletion.reason = reason
        assert rescue_sop_fx.mark_for_deletion.reason == reason

        rescue_sop_fx.mark_for_deletion.reporter = reporter
        assert rescue_sop_fx.mark_for_deletion.reporter == reporter


    @pytest.mark.parametrize("reason,reporter,marked", [
        ([], 42.2, -1),
        (-2.1, {"Potato"}, None),
        ([], 42, "md reason"),
        (True, -42.2, uuid4())
    ])
    def test_mark_for_deletion_setter_bad_data(self, reason: str or None, reporter: str or None,
                                               marked: bool, rescue_sop_fx: Rescue):
        """
        Verifies setting the mark for deletion property succeeds when the data is valid

        Args:
            rescue_sop_fx (): plain rescue fixture
            reason (str): md reason
            reporter(str) md reporter
        """
        with pytest.raises(TypeError):
            rescue_sop_fx.mark_for_deletion.reason = reason

        with pytest.raises(TypeError):
            rescue_sop_fx.mark_for_deletion.reporter = reporter

        with pytest.raises(TypeError):
            rescue_sop_fx.mark_for_deletion.marked = marked

        assert rescue_sop_fx.mark_for_deletion.marked is False
        assert rescue_sop_fx.mark_for_deletion.reason != reason
        assert rescue_sop_fx.mark_for_deletion.reporter != reporter

    @pytest.mark.parametrize("garbage", [None, 42, -2.2, []])
    def test_mark_for_deletion_setter_bad_types(self, garbage, rescue_plain_fx: Rescue):
        """Verifies attempting to set Rescue.mark_for_deletion to bad types results in a TypeError"""
        myRescue = deepcopy(rescue_plain_fx)

        with pytest.raises(TypeError):
            myRescue.mark_for_deletion = garbage

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uuid,name", [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")])
    async def test_add_rat_by_rat_object(self, uuid: uuid4, name: str, rescue_plain_fx: Rescue):
        """
        Verifies `Rescue.add_rat` can add a rat given a `Rats` object
        """
        # rats_raw = [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")]
        # rats = [Rats(x, y) for x, y in rats_raw]

        myRescue = deepcopy(rescue_plain_fx)

        rat = Rats(uuid=uuid, name=name)

        await myRescue.add_rat(rat=rat)

        assert rat in myRescue.rats

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uuid,name", [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")])
    async def test_add_rat_by_uuid(self, uuid: uuid4, name: str, rescue_plain_fx: Rescue):
        """
        Verifies `Rescue.add_rat` can add a rat given a guid and a name
        """
        myRescue = deepcopy(rescue_plain_fx)

        await myRescue.add_rat(name=name, guid=uuid)

        assert name in Rats.cache_by_name

    def test_eq_none(self, rescue_plain_fx: Rescue):
        """Verifies behavior of `Rescue.__eq__` when comparing against None"""
        # This check only exists because this object is nullable...
        # and no, you really shouldn't be comparing against None like this.
        assert not None == rescue_plain_fx

    def test_eq_bad_type(self, rescue_plain_fx: Rescue):
        """
        Verifies Rescue.__eq__ raises a type error when attempting to compare something
            other than a rescue.
        """
        assert not rescue_plain_fx == "Rescue object at <0xBADBEEF> "

    @pytest.mark.parametrize("words, words_eol", [
        (["md", "3", "I", "have", "my", "reasons!"],
         ["3 I have my reasons!", "I have my reasons!", "have my reasons!",
          "my reasons!", "reasons!"]),
        (["md", "4", "reasons"], ["md 4 reasons", "4 reasons", "reasons"])
    ])
    def test_mark_true_valid(self, rescue_sop_fx: Rescue,
                             bot_fx,
                             user_fx: User,
                             words: List[str],
                             words_eol: List[str]):
        """Verifies Rescue.mark functions as expected when marking a case for deletion"""

        context = Context(bot_fx,
                          user_fx,
                          "#unit_test", words, words_eol)

        rescue_sop_fx.mark(True, context)
        assert rescue_sop_fx.mark_for_deletion.marked
        assert user_fx.nickname == rescue_sop_fx.mark_for_deletion.reporter
        assert context.words_eol[1] == rescue_sop_fx.mark_for_deletion.reason
