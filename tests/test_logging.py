"""
test_logging.py

Tests for the logging module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging
import random


def random_string():
    """
    Creates a 16 digit alphanumeric string.  For use
    with logging tests.

    Returns:
         16 digit alphanumeric string.
    """
    source = "abcdefghijklmnopqrstuvwxyz012345" \
             "67890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string_len = 16
    result = "".join(random.sample(source, string_len))
    return result


def test_logging_default_level(Logging_fx):
    """
    Test logging level has been set to INFO by default
    """
    assert Logging_fx.getEffectiveLevel() == logging.INFO


def test_logging_console_debug(caplog, Logging_fx):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = random_string()
    Logging_fx.setLevel(logging.DEBUG)
    Logging_fx.debug(f"Console Test String {test_randstring}")

    assert caplog.record_tuples == [
        ('mecha', logging.DEBUG, f"Console Test String {test_randstring}"),
    ]


def test_logging_console_info(caplog, Logging_fx):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = random_string()
    Logging_fx.info(f"Console Test String {test_randstring}")

    assert caplog.record_tuples == [
        ('mecha', logging.INFO, f"Console Test String {test_randstring}"),
    ]


def test_logging_console_warn(caplog, Logging_fx):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = random_string()
    Logging_fx.warn(f"Console Test String {test_randstring}")

    assert caplog.record_tuples == [
        ('mecha', logging.WARN, f"Console Test String {test_randstring}"),
    ]


def test_logging_console_error(caplog, Logging_fx):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = random_string()
    Logging_fx.error(f"Console Test String {test_randstring}")

    assert caplog.record_tuples == [
        ('mecha', logging.ERROR, f"Console Test String {test_randstring}"),
    ]


def test_logging_to_file_debug(Logging_fx):
    """
    Test log file input matches written data by logging a random string,
    and then searching that file for the string.
    """
    test_randstring = random_string()

    Logging_fx.setLevel(logging.DEBUG)
    Logging_fx.debug(f"File Test String {test_randstring}")

    re_match = 0
    for line in open('logs/unit_tests.log'):
        if test_randstring in line:
            re_match += 1

    assert re_match == 2


def test_logging_to_file_info(Logging_fx):
    """
    Test log file input matches written data by logging a random string,
    and then searching that file for the string.
    """
    test_randstring = random_string()

    Logging_fx.info(f"File Test String {test_randstring}")

    re_match = 0
    for line in open('logs/unit_tests.log'):
        if test_randstring in line:
            re_match += 1

    assert re_match == 2
