"""
test_logging.py

Tests for the logging module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

import pytest


def log_severity_call(logger, severity, random_string):
    logging_string = f"Test String {random_string}"
    if severity == logging.DEBUG:
        logger.debug(logging_string)
    elif severity == logging.INFO:
        logger.info(logging_string)
    elif severity == logging.WARN:
        logger.warn(logging_string)
    elif severity == logging.ERROR:
        logger.error(logging_string)


def test_logging_default_level(Logging_fx):
    """
    Test logging level has been set to INFO by default
    """
    Logging_fx.setLevel(logging.INFO)
    assert Logging_fx.getEffectiveLevel() == logging.INFO


@pytest.mark.parametrize("severity", [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR])
def test_logging_levels(caplog, Logging_fx, Random_string_fx, severity):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = Random_string_fx
    Logging_fx.setLevel(severity)
    log_severity_call(Logging_fx, severity, test_randstring)

    assert caplog.record_tuples == [
        ('mecha', severity, f"Test String {test_randstring}"),
    ]


@pytest.mark.parametrize("severity", [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR])
def test_logging_to_file_debug(Logging_fx, Random_string_fx, severity):
    """
    Test log file input matches written data by logging a random string,
    and then searching that file for the string.
    """
    test_randstring = Random_string_fx

    Logging_fx.setLevel(severity)
    log_severity_call(Logging_fx, severity, test_randstring)

    match = 0
    for line in open('logs/unit_tests.log'):
        if test_randstring in line:
            match += 1

    assert 1 == match
