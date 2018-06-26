import pytest

import utils.ratlib

pytestmark = pytest.mark.ratlib

nickname_test_list = [
    ('ThisIsATest[BOT]', "ThisIsATest"),
    ('firehawk2421', 'firehawk2421'),
    ('xBoxRulz1911[xb|nd]', 'xBoxRulz1911'),
    ('Shatt[PC|afk]', 'Shatt')
]

sanitize_test_list = [
    ('4Red Text,12,', 'Red Text,12,'),
    ('4,4Red Text on Red B@ckground', 'Red Text on Red B@ckground'),
    ('10,10Lorem ipsum dolor sit amet', 'Lorem ipsum dolor sit amet'),
    ('Bold Text;;;', 'Bold Text'),
    ('Bold Italic Text', 'Bold Italic Text'),
    ('4Bold Red Text', 'Bold Red Text'),
    ('Um die Rats zu deiner Freundesliste hinzuzufügen drücke',
     'Um die Rats zu deiner Freundesliste hinzuzufügen drücke'),
    ('которые отдают топливо, нажмите здесь: http://t.fuelr.at/kgbfoamru',
     'которые отдают топливо, нажмите здесь: http://t.fuelr.at/kgbfoamru'),
    ('a;A;B;b;C;c;1\'2\'3', 'aABbCc123'),
    ('!inject 99 5:30 o2 remaining', '!inject 99 5:30 o2 remaining'),
    (',Banana', 'Banana'),
    ('137Banana', 'Banana'),
    (',Banana', ',Banana'),
    ('13,15Banana', 'Banana')
]


@pytest.mark.parametrize("nickname, expected", nickname_test_list)
def test_strip_name(nickname, expected):
    """
    Verifies nicknames are properly stripped.  Rewrite into pytest from unit test.
    """
    assert utils.ratlib.strip_name(nickname) == expected


@pytest.mark.parametrize("input_message, expected_message", sanitize_test_list)
def test_sanitize(input_message, expected_message):
    """
    Verifies sanitize routine is properly removing string elements.
    """
    assert utils.ratlib.sanitize(input_message) == expected_message
