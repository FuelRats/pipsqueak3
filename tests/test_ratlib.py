import pytest

import utils.ratlib
from utils.ratlib import Singleton
from utils.ratlib import Colors, Formatting, color, bold, underline, italic, reverse

pytestmark = pytest.mark.ratlib

nickname_test_list = [
    ('ThisIsATest[BOT]', "ThisIsATest"),
    ('firehawk2421', 'firehawk2421'),
    ('xBoxRulz1911[xb|nd]', 'xBoxRulz1911'),
    ('Shatt[PC|afk]', 'Shatt')
]

SANITIZE_TEST_LIST = [
    ('Um die Rat zu deiner Freundesliste hinzuzufügen drücke',
     'Um die Rat zu deiner Freundesliste hinzuzufügen drücke'),
    ('которые отдают топливо, нажмите здесь: http://t.fuelr.at/kgbfoamru',
     'которые отдают топливо, нажмите здесь: http://t.fuelr.at/kgbfoamru'),
    ('!inject 99 5:30 o2 remaining', '!inject 99 5:30 o2 remaining'),
    ('\tTab\tbing\tton', 'Tabbington'),
    ('Strikethrough', 'Strikethrough'),
    ('Underline', 'Underline'),
    ('Monospace', 'Monospace'),
    ('Reverse', 'Reverse'),
    ('Reset', 'Reset'),
    ('Bold Text', 'Bold Text'),
    ('Bold Italic Text', 'Bold Italic Text'),
    ('4Bold Red Text', 'Bold Red Text'),
    (',Banana', ',Banana'),
    ('137Banana', '7Banana'),
    ('4Red Text,12,', 'Red Text,12,'),
    ('4,4Red Text on Red B@ckground', 'Red Text on Red B@ckground'),
    ('10,10Lorem ipsum dolor sit amet', 'Lorem ipsum dolor sit amet'),
    ('04Red 03Green 02Blue', 'Red Green Blue'),
    ('13,Banana', ',Banana'),
    ('13,01Banana', 'Banana'),
    (',Banana', ',Banana'),
    ('13,15Banana', 'Banana'),
    (',15Banana', ',15Banana'),
    ('Bold Italic Underline', 'Bold Italic Underline'),
    ('HexColor', 'HexColor'),
    ('fFa5DCBanana', 'Banana'),
    ('ffffff,000000Banana', 'Banana'),
    ('123456,Banana', ',Banana'),
    ('FF0000Red 00fF00Green 0000ffBlue', 'Red Green Blue'),
    ('no 4ite56AdcBms2, fo\tx onlyFF66AA, final des\tt555555ination',
     'no items, fox only, final destination')
]


@pytest.mark.parametrize("nickname, expected", nickname_test_list)
def test_strip_name(nickname, expected):
    """
    Verifies nicknames are properly stripped.  Rewrite into pytest from unit test.
    """
    assert utils.ratlib.strip_name(nickname) == expected


@pytest.mark.parametrize("input_message, expected_message", SANITIZE_TEST_LIST)
def test_sanitize(input_message, expected_message):
    """
    Verifies sanitize routine is properly removing string elements.
    """
    assert utils.ratlib.sanitize(input_message) == expected_message


def test_singleton_direct_inheritance():
    """
    Verifies the Singleton class behaves as expected for classes directly inheriting
    """

    class Potato(Singleton):
        pass

    # noinspection PyUnresolvedReferences
    assert Potato._instance is None
    foo = Potato()
    bar = Potato()
    assert foo is bar
    # noinspection PyUnresolvedReferences
    assert Potato._instance is foo


def test_singleton_indirect_inheritance():
    """
    Verifies the Singleton class behaves as expected for classes ultimately derived from Singleton
    """

    class Potato(Singleton):
        pass

    class Snafu(Potato):
        pass

    # noinspection PyUnresolvedReferences
    assert Snafu._instance is None
    foo = Snafu()
    bar = Snafu()
    assert foo is bar
    # noinspection PyUnresolvedReferences
    assert Snafu._instance is foo


@pytest.mark.parametrize("expected_color", (Colors.RED, Colors.BLUE, Colors.BLACK, Colors.GREEN))
def test_color_single_color(expected_color, random_string_fx):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_COLOR.value}{expected_color}{test_string}" \
           f"{Formatting.FORMAT_COLOR.value}" == color(test_string, expected_color)


@pytest.mark.parametrize("expected_color,expected_bg_color", (
                        (Colors.RED, Colors.ORANGE),
                        (Colors.BROWN, Colors.BLUE),
                        (Colors.YELLOW, Colors.GREY)
                        ))
def test_color_background_color(random_string_fx, expected_color, expected_bg_color):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_COLOR.value}{expected_color},{expected_bg_color}{test_string}" \
           f"{Formatting.FORMAT_COLOR.value}" == color(test_string,
                                                       expected_color,
                                                       expected_bg_color)


def test_color_bold(random_string_fx):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_BOLD.value}{test_string}{Formatting.FORMAT_BOLD.value}" \
           == bold(test_string)


def test_color_italic(random_string_fx):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_ITALIC.value}{test_string}{Formatting.FORMAT_ITALIC.value}" == \
           italic(test_string)


def test_color_underline(random_string_fx):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_UNDERLINE.value}{test_string}{Formatting.FORMAT_UNDERLINE.value}" \
           == underline(test_string)


def test_color_reverse(random_string_fx):
    test_string = random_string_fx
    assert f"{Formatting.FORMAT_REVERSE.value}{test_string}{Formatting.FORMAT_REVERSE.value}" \
           == reverse(test_string)
