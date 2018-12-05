"""
test_rescue.py - tests for Rescue and RescueBoard objects

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pytest
from copy import deepcopy
from datetime import datetime
from uuid import uuid4, UUID
from Modules.epic import Epic
from Modules.mark_for_deletion import MarkForDeletion
from Modules.rat import Rat
from Modules.rat_rescue import Rescue
from Modules.rat_cache import RatCache, Platforms
from utils.ratlib import Status

pytestmark = pytest.mark.rescue


@pytest.mark.parametrize("expected_client", ['DeadBeef', 'Commander_Test', '11Alpha1',
                                             'Xxx22K1ng2xxX'])
def test_verify_rescue_client(rescue_plain_fx, expected_client):
    """
    Verify Rescue.client returns expected value.
    """
    rescue_plain_fx.client = expected_client
    assert rescue_plain_fx.client == expected_client


@pytest.mark.parametrize("expected_system", ['Nuekau YU-F d11-176', 'Eidairld RN-J d9-7',
                                             'Wredguia LI-G b38-1', 'Tyriedgoo CR-N c6-0'])
def test_verify_rescue_system(rescue_plain_fx, expected_system):
    """
    Verify Rescue.system returns expected value.
    """
    rescue_plain_fx.system = expected_system
    expected_system = expected_system.upper()
    assert rescue_plain_fx.system == expected_system


@pytest.mark.parametrize("expected_irc_nickname", ['MasterToNone', 'White Sheets',
                                                   'Utopia27', 'LintHair'])
def test_verify_expected_irc_nickname(rescue_plain_fx, expected_irc_nickname):
    """
    Verify Rescue.irc_nickname returns expected value.
    """
    rescue_plain_fx.irc_nickname = expected_irc_nickname
    assert rescue_plain_fx.irc_nickname == expected_irc_nickname


def test_verify_expected_ratboard(rescue_sop_fx, rat_board_fx):
    """
    Verify rescue, when appended, is contained within the Ratboard object.
    """
    rat_board_fx.append(rescue_sop_fx)
    assert rescue_sop_fx in rat_board_fx


def test_validate_rescue_uuid(rescue_sop_fx):
    """
    Validates the UUID of rescue_sop_fx._id
    """
    result = UUID(rescue_sop_fx._api_id.hex, version=4)
    assert rescue_sop_fx.uuid == result


def test_client_is_set(rescue_sop_fx):
    """
    Verifies that rescue_sop_fx._client is set.
    """
    assert rescue_sop_fx.client != ''


def test_created_at_date_exists(rescue_sop_fx):
    """
    Verifies rescue.created_at datetime is set, and in the past.
    """
    expected_time_differential = (datetime.utcnow() - rescue_sop_fx.created_at)
    assert expected_time_differential != 0


def test_updated_at_date_exists(rescue_sop_fx):
    """
    Verifies rescue.updated_at is correct
    """
    rescue_sop_fx._updatedAt = datetime(1990, 1, 1, 1, 1, 1)

    with rescue_sop_fx.change():
        rescue_sop_fx.system = 'UpdatedSystem'

    assert rescue_sop_fx.updated_at != datetime(1990, 1, 1, 1, 1, 1)


def test_updated_at_raises_typeerror(rescue_sop_fx):
    """
    Verify Rescue.updated_at raises TypeError if given incorrect value,
    or is set to a date in the past.
    """
    rescue_sop_fx._createdAt = datetime(1991, 1, 1, 1, 1, 1,)

    # Set to a string time
    with pytest.raises(TypeError):
        rescue_sop_fx.updated_at = '07:32:01 4-4-2063'

    # Set to the past:
    with pytest.raises(ValueError):
        rescue_sop_fx.updated_at = datetime(1990, 1, 1, 1, 1, 1)


@pytest.mark.parametrize("expected_rats", [['Joeblow', 'TinyTim', 'White Sheets'],
                                           ['Azel4st', 'Aero_Chamber', 'YoMama_27'],
                                           ['UnitTestingSucks', 'PytestPwns', 'yUnoComplain']])
def test_unidentified_rats_list(rescue_plain_fx, expected_rats):
    """
    Verifies a list of unidentified rats is set, and returned.

    Uses expected_rats list cast as set to determine if all values match,
    by intersection.  If all values match, the assertion is true.  If not all values
    match, a set of matches is returned, or false if no matches.

    Either a returned set or a false assertion will fail this test.
    """
    rescue_plain_fx.unidentified_rats = expected_rats
    assert set(expected_rats).intersection(rescue_plain_fx.unidentified_rats)


def test_rescue_defaults_to_active(rescue_sop_fx):
    """
    Set rescue.active to false, and verify.
    (inverse test)
    """
    rescue_sop_fx.active = False
    assert not rescue_sop_fx.active


def test_rescue_rat_setter_typeerror(rescue_sop_fx):
    """
    Verifies the Rescue.rats setter returns a TypeError when not given proper value.
    This is NOT the proper way to modify rats in production, use Rescue.add_rat.
    """
    # Set without error, expected type
    rescue_sop_fx.rats = ['SomeRat', 'AnotherRat', 'NeedsTail']

    with pytest.raises(TypeError):
        rescue_sop_fx.rats = 'Some Rat Another Rat Needs My Tail'


@pytest.mark.parametrize("expected_quote, expected_author", [('5 min o2', 'BadAzz'),
                                                             ('2600LS from star', 'Unzolver'),
                                                             ('1:30 o2, client @station', 'T3str')]
                         )
def test_rescue_quotes_list(rescue_sop_fx, expected_quote, expected_author):
    """
    Verifies quotes are added and returned properly.
    """
    # Add Quote
    rescue_sop_fx.add_quote(expected_quote, expected_author)

    # Check if Quote/Author match.
    for quote in rescue_sop_fx.quotes:
        assert quote.message == expected_quote
        assert quote.author == expected_author


def test_rescue_quotes_without_author(rescue_sop_fx):
    """
    Verify quote is accepted without an author.
    """
    # Define and add quote
    expected_quote = 'Houston, we have a problem'
    rescue_sop_fx.add_quote(expected_quote)

    # Check the quote we added is correct.
    for quote in rescue_sop_fx.quotes:
        assert quote.message == expected_quote


def test_rescue_quotes(rescue_sop_fx):
    """
    Verifies quotes receives and returns a list.  Should return
    a ValueError if the incorrect type is supplied.

    This is NOT normally set, in production use .add_quote
    """
    expected_quotes = ['This is a quote', 'Here is another Quote']
    rescue_sop_fx.quotes = expected_quotes
    assert rescue_sop_fx.quotes == expected_quotes

    with pytest.raises(ValueError):
        rescue_sop_fx.quotes = 'I like Trains, Some Kid, 2010'


def test_epic_rescue_attached(epic_fx):
    """
    Verifies attached epic object referenced by rescue is the same object, and
    that only one rescue has been added.
    """
    # Create local rescue object
    test_rescue = Rescue(uuid4(), 'TestClient', 'Alioth', 'Test_Client', epic=[epic_fx])

    # One rescue added, the List should return only ONE Epic.
    assert len(test_rescue.epic) == 1

    # Check that the epic object in list is epic_fx
    assert test_rescue.epic[0] is epic_fx


@pytest.mark.parametrize('expected_title', ['Operation Unit Hazing', 'Dumbo Drop', 'Delight'])
def test_rescue_title(rescue_sop_fx, expected_title):
    """
    Verifies title is unset by default, and verifies new title is reflected.
    """
    assert rescue_sop_fx.title is None

    # Set a title
    rescue_sop_fx.title = expected_title

    # Assert again
    assert rescue_sop_fx.title == expected_title


def test_rescue_title_type_error(rescue_sop_fx):
    """
    Verifies Rescue.Title returns a TypeError not passed 'None' or str.
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.title = ['Garbage', 'Pail']

    # Causing an Error when Rescue.title = None fails:
    rescue_sop_fx.title = None


def test_rescue_first_limpet(rescue_sop_fx, rat_good_fx):
    """
    Verifies first limpet is set and returned properly.
    """
    # Pass UUID to first_limpet
    rescue_sop_fx.first_limpet = rat_good_fx.uuid
    assert rescue_sop_fx.first_limpet == rat_good_fx.uuid

    # Pass something immutable and verify the coercion into UUID fails,
    # raising a TypeError from Rescue module
    with pytest.raises(TypeError):
        rescue_sop_fx.first_limpet = rat_good_fx


def test_rescue_board_index(rescue_plain_fx):
    """
    Verifies board index is NOT set without a rescue attached
    """
    # Do not set board index
    test_rescue = Rescue(uuid4(), 'Test_Client', 'AliothJr', 'TestClient')
    assert test_rescue.board_index is None

    # Add rescue fixture
    test_rescue = rescue_plain_fx
    assert test_rescue.board_index == 42

    # Add a negative int for board index, ensuring ValueError is thrown
    with pytest.raises(ValueError):
        test_rescue.board_index = -99

    # Add incorrect type, ensuring TypeError is thrown
    with pytest.raises(TypeError):
        test_rescue.board_index = 'Index!'


def test_marked_for_deletion(mark_for_deletion_plain_fx, mark_for_deletion_fx, rescue_plain_fx):
    """
    Verifies MFD object is settable and returns proper data
    """
    # Verify linkage
    rescue_plain_fx.marked_for_deletion = mark_for_deletion_plain_fx
    assert not rescue_plain_fx.marked_for_deletion.marked

    # Build test MFD Object
    test_mark_for_deletion = mark_for_deletion_fx

    # Verify Test MFD Object
    rescue_plain_fx.marked_for_deletion = test_mark_for_deletion
    assert rescue_plain_fx.marked_for_deletion.marked == mark_for_deletion_fx.marked
    assert rescue_plain_fx.marked_for_deletion.reporter == mark_for_deletion_fx.reporter
    assert rescue_plain_fx.marked_for_deletion.reason == mark_for_deletion_fx.reason


def test_marked_for_deletion_type_errors(rescue_plain_fx):
    """
    Verifies TypeError is thrown when the wrong type is passed to MFD
    """
    # Check TypeError Assertion
    with pytest.raises(TypeError):
        rescue_plain_fx.marked_for_deletion = ['Improper List']

    with pytest.raises(TypeError):
        rescue_plain_fx.marked_for_deletion = 'This is not a valid reason'

    with pytest.raises(TypeError):
        rescue_plain_fx.marked_for_deletion = {'Reason 123': 'Bowl of Petunias'}


def test_rescue_lang_id_constructor(rescue_sop_fx):
    """
    Verifies Language_ID is returned
    """
    # Defaults to EN
    assert rescue_sop_fx.lang_id == 'EN'


@pytest.mark.parametrize("garbage", [None, 42, -2.2, uuid4()])
def test_lang_id_garbage(garbage, rescue_plain_fx: Rescue):
    """
    Verifies throwing garbage types at Rescue.lang_id results in a TypeError
    Args:
        garbage (): Garbage to throw
        rescue_plain_fx (Rescue): Plain rescue Fixture
    """
    with pytest.raises(TypeError):
        rescue_plain_fx.lang_id = garbage


def test_platform_raises_type_error(rescue_sop_fx):
    """
    Verifies that Rescue.Platform properly raises a TypeError when the
    wrong value is supplied.
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.platform = 'Xbox'


@pytest.mark.asyncio
async def test_add_rats_bad_id(rat_no_id_fx, rescue_sop_fx):
    """
    Verifies attempting to add a rat that does not have a API id fails as expected
    """
    with pytest.raises(ValueError, message="Assigned rat does not have a known API ID"):
        await rescue_sop_fx.add_rat(rat=rat_no_id_fx)
        assert rat_no_id_fx not in rescue_sop_fx.rats


@pytest.mark.asyncio
async def test_add_rats_ok(rat_good_fx, rescue_sop_fx):
    """
        Verifies adding a existing rat with a UUID works
        Args:
            rat_good_fx (Rat): Good Rat object Test Fixture
            rescue_sop_fx (Rescue):  Rescue object Test Fixture
    """
    # rescue_sop_fx:Rescue
    await rescue_sop_fx.add_rat(rat=rat_good_fx)
    assert rat_good_fx in rescue_sop_fx.rats


@pytest.mark.asyncio
async def test_add_rat_from_cache(rat_good_fx: Rat, rescue_sop_fx: Rescue):
    """
    Verifies rat added from cache matches rat object in Rescue
    """
    await rescue_sop_fx.add_rat(rat_good_fx.name)
    assert rat_good_fx == rescue_sop_fx.rats[0]


@pytest.mark.parametrize("garbage", [(None), (42), (-2.2), (uuid4())])
def test_irc_nickname_garbage(garbage, rescue_plain_fx: Rescue):
    """
    Verifies throwing garbage types at Rescue.irc_nickname results in a TypeError

       Args:
            garbage (): Garbage to throw
            rescue_plain_fx (Rescue): Plain rescue Fixture
    """
    with pytest.raises(TypeError):
        rescue_plain_fx.irc_nickname = garbage


@pytest.mark.parametrize("test_input", ["foo", "bar", "en-us", "RU-RU"])
def test_irc_nickname_strings(test_input, rescue_plain_fx: Rescue):
    """
    Verifies the irc nickname can be set when passed a string

        Args:
            test_input (str): values to test
            rescue_plain_fx (Rescue): Rescue fixture

    """

    rescue_plain_fx.irc_nickname = test_input
    assert rescue_plain_fx.irc_nickname == test_input


@pytest.mark.parametrize("garbage", [None, 42, -2.2, uuid4()])
def test_lang_id_garbage(garbage, rescue_plain_fx: Rescue):
    """
    Verifies throwing garbage types at Rescue.lang_id results in a TypeError

        Args:
            garbage (): Garbage to throw
            rescue_plain_fx (Rescue): Plain rescue Fixture
    """
    with pytest.raises(TypeError):
        rescue_plain_fx.lang_id = garbage


@pytest.mark.parametrize("test_input", ["foo", "bar", "en-us", "RU-RU"])
def test_lang_id_strings(test_input, rescue_plain_fx: Rescue):
    """
    Verifies the lang id can be set when passed a string

        Args:
            test_input (str): values to test
            rescue_plain_fx (Rescue): Rescue fixture

    """

    rescue_plain_fx.lang_id = test_input
    assert rescue_plain_fx.lang_id == test_input


def test_set_unidentified_rats_garbage_in_list(rescue_plain_fx: Rescue):
    """
    Verifies a ValueError is raised if the list passed to Rat.unidentified_Rats contains
    illegal values
    """
    garbage = [12, -42.2, None]
    with pytest.raises(ValueError):
        rescue_plain_fx.unidentified_rats = garbage


def test_set_unidentified_rats_incorrect_type(rescue_plain_fx: Rescue):
    """
    Verifies a TypeError is raised if another type other than list is passed.
    """
    with pytest.raises(TypeError):
        rescue_plain_fx.unidentified_rats = 'Snozzberry, Wonka, Doc'


@pytest.mark.parametrize("reason,reporter,marked", [
    ([], 42.2, -1),
    (-2.1, {"Potato"}, None),
    ([], 42, "md reason"),
    (True, -42.2, uuid4())
])
def test_mark_for_deletion_setter_bad_data(reason: str or None, reporter: str or None,
                                           marked: bool, rescue_sop_fx: Rescue):
    """
    Verifies setting the mark for deletion property succeeds when the data is valid

        Args:
            rescue_sop_fx (): plain rescue fixture
            reason (str): md reason
            reporter(str) md reporter
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.marked_for_deletion.reason = reason

    with pytest.raises(TypeError):
        rescue_sop_fx.marked_for_deletion.reporter = reporter

    with pytest.raises(TypeError):
        rescue_sop_fx.marked_for_deletion.marked = marked

    assert rescue_sop_fx.marked_for_deletion.marked is False
    assert rescue_sop_fx.marked_for_deletion.reason != reason
    assert rescue_sop_fx.marked_for_deletion.reporter != reporter


@pytest.mark.parametrize("garbage", [None, 42, -2.2, []])
def test_mark_for_deletion_setter_bad_types(garbage, rescue_plain_fx: Rescue):
    """
    Verifies attempting to set Rescue.mark_for_deletion to bad types results in a TypeError
    """
    result_rescue = deepcopy(rescue_plain_fx)

    with pytest.raises(TypeError):
        result_rescue.marked_for_deletion = garbage


@pytest.mark.asyncio
@pytest.mark.parametrize("uuid,name", [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")])
async def test_add_rat_by_rat_object(uuid: UUID, name: str, rescue_plain_fx: Rescue):
    """
    Verifies `Rescue.add_rat` can add a rat given a `Rat` object
    """
    # rats_raw = [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")]
    # rats = [Rat(x, y) for x, y in rats_raw]

    result_rescue = deepcopy(rescue_plain_fx)

    rat = Rat(uuid=uuid, name=name)

    await result_rescue.add_rat(rat=rat)

    assert rat in result_rescue.rats


@pytest.mark.asyncio
@pytest.mark.parametrize("uuid,name", [(uuid4(), "foo"), (uuid4(), "bar"), (uuid4(), "potato")])
async def test_add_rat_by_uuid(uuid: UUID, name: str, rescue_plain_fx: Rescue, rat_cache_fx):
    """
    Verifies `Rescue.add_rat` can add a rat given a guid and a name
    """
    result_rescue = deepcopy(rescue_plain_fx)

    await result_rescue.add_rat(name=name, guid=uuid)

    assert name in rat_cache_fx.by_name


@pytest.mark.asyncio
async def test_add_rat_returns_rat_by_object(rat_good_fx: Rat, rescue_plain_fx: Rescue):
    """
    Verifies `Rescue.add_rat` returns a proper `Rat` object when given a valid Rat object
    """
    result = await rescue_plain_fx.add_rat(rat=rat_good_fx)

    assert result is rat_good_fx


@pytest.mark.asyncio
async def test_add_rat_returns_rat_by_name(rat_cache_fx, rescue_plain_fx: Rescue, rat_good_fx: Rat):
    """
    Verifies `Rescue.add_rat` returns a proper `Rat` object when given a valid name of a rat
    """
    # add our test rat to the cache so add_rat can find it
    rat_cache_fx.by_name[rat_good_fx.name] = rat_good_fx

    result = await rescue_plain_fx.add_rat(name=rat_good_fx.name)

    assert result is rat_good_fx


@pytest.mark.asyncio
async def test_add_rat_returns_rat_by_uuid(rat_cache_fx, rescue_plain_fx: Rescue, rat_good_fx: Rat):
    """
    Verifies `Rescue.add_rat` returns a proper `Rat` object when given a valid UUID of a rat
    """
    # add our test rat to the cache so add_rat can find it
    rat_cache_fx.by_uuid[rat_good_fx.uuid] = rat_good_fx

    result = await rescue_plain_fx.add_rat(guid=rat_good_fx.uuid)

    assert result is rat_good_fx


@pytest.mark.asyncio
async def test_add_rat_returns_rat_by_uuid_string(rat_cache_fx,
                                                  rescue_plain_fx: Rescue,
                                                  rat_good_fx: Rat):
    """
    Verifies `Rescue.add_rat` returns a proper `Rat` object when given a valid UUID string of a rat
    """
    # add our test rat to the cache so add_rat can find it
    rat_cache_fx.by_uuid[rat_good_fx.uuid] = rat_good_fx

    result = await rescue_plain_fx.add_rat(guid=str(rat_good_fx.uuid))

    assert result is rat_good_fx


def test_eq_none(rescue_plain_fx: Rescue):
    """
    Verifies behavior of `Rescue.__eq__` when comparing against None
    """
    # This check only exists because this object is nullable...
    # and no, you really shouldn't be comparing against None like this.
    assert not None == rescue_plain_fx


def test_eq_bad_type(rescue_plain_fx: Rescue):
    """
    Verifies Rescue.__eq__ raises a type error when attempting to compare something
    other than a rescue.
    """
    assert not rescue_plain_fx == "Rescue object at <0xBADBEEF> "


@pytest.mark.parametrize("reporter, reason", [("unit_test[BOT]", "reasons! reasons i say!"),
                                              ("potato[pc|nd]", "uhhh..."),
                                              ("sayWhat99", "dawg this ain't right!")])
def test_mark_delete_valid(rescue_sop_fx: Rescue, reporter: str, reason: str):
    """
    Verifies Rescue.mark functions as expected when marking a case for deletion
    """

    rescue_sop_fx.mark_delete(reporter, reason)

    assert rescue_sop_fx.marked_for_deletion.marked
    assert reporter == rescue_sop_fx.marked_for_deletion.reporter
    assert reason == rescue_sop_fx.marked_for_deletion.reason


def test_mark_delete_invalid(rescue_sop_fx: Rescue):
    """
    Verify what happens when garbage gets thrown at `rescue.mark`
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.mark_delete(None, "sna")

        with pytest.raises(TypeError):
            rescue_sop_fx.mark_delete("sna", None)

        with pytest.raises(ValueError):
            rescue_sop_fx.mark_delete("unit_test", "")
            

def test_mark_for_deletion_unset(rescue_sop_fx: Rescue):
    """
    Verify unmarking a case that was MD'ed works as expected
    """
    rescue_sop_fx.marked_for_deletion = MarkForDeletion(True, "unit_test[BOT]",
                                                        "unit test reasons!")

    rescue_sop_fx.unmark_delete()
    assert rescue_sop_fx.marked_for_deletion.marked is False
    assert rescue_sop_fx.marked_for_deletion.reporter is None
    assert rescue_sop_fx.marked_for_deletion.reason is None


def test_rescue_status_default(rescue_sop_fx):
    """
    Verifies rescue status defaults to Status.OPEN
    """
    # Default
    assert rescue_sop_fx.status == Status.OPEN

    # Test Getter
    assert rescue_sop_fx.open


def test_rescue_open_setter_helper(rescue_sop_fx):
    """
    Verifies passing a bool to Rescue.open properly sets
    Rescue.status
    """
    rescue_sop_fx.open = True
    assert rescue_sop_fx.open


def test_rescue_open_setter_helper2(rescue_sop_fx):
    """
    Verifies passing a bool to Rescue.open properly sets
    Rescue.status
    """
    rescue_sop_fx.open = False
    assert rescue_sop_fx.open is False


def test_rescue_open_type_error(rescue_sop_fx):
    """
    Verifies a TypeError is raised if Rescue.Open is passed a
    non-bool.
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.open = 'Yes'


@pytest.mark.parametrize("expected_status", [Status.OPEN, Status.CLOSED, Status.INACTIVE])
def test_rescue_status_enum(rescue_sop_fx, expected_status):
    """
    Verifies all rescue status returns properly.
    """
    rescue_sop_fx.status = expected_status
    assert rescue_sop_fx.status == expected_status


def test_rescue_status_type_error(rescue_sop_fx):
    """
    Verifies a TypeError is raised if an incorrect status value is cast.
    """
    with pytest.raises(TypeError):
        rescue_sop_fx.status = 'EN'


def test_rescue_active_setter(rescue_sop_fx):
    """
    Verify Rescue is Active by default, set it to False,
    and verify TypeError is cast if a non-bool is sent.
    """
    # Default state
    assert rescue_sop_fx.active

    # Set Inactive directly
    rescue_sop_fx.active = False
    assert not rescue_sop_fx.active

    # Set Active directly
    rescue_sop_fx.active = True
    assert rescue_sop_fx

    # Set Active by status update
    rescue_sop_fx.status = Status.OPEN
    assert rescue_sop_fx.active

    # Set Inactive by status update
    rescue_sop_fx.status = Status.INACTIVE

    with pytest.raises(ValueError):
        rescue_sop_fx.active = 'Yes'


def test_rescue_code_red_default(rescue_sop_fx):
    """
    Verifies CR is false by default.
    """
    assert not rescue_sop_fx.code_red


def test_rescue_code_red_setter(rescue_sop_fx):
    """
    Verifies code_red is writable and a TypeError is raised if a non-bool
    value is passed.
    """
    rescue_sop_fx.code_red = True
    assert rescue_sop_fx.code_red

    with pytest.raises(TypeError):
        rescue_sop_fx.code_red = 'Yes'
