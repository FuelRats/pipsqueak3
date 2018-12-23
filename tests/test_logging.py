"""
test_logging.py

Tests for the logging module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging
import tempfile
import os

import pytest

pytestmark = pytest.mark.logging


def log_severity_call(logger, severity, random_string):
    logging_string = f"Test String {random_string}"
    if severity == logging.DEBUG:
        logger.debug(logging_string)
    elif severity == logging.INFO:
        logger.info(logging_string)
    elif severity == logging.WARN:
        logger.warning(logging_string)
    elif severity == logging.ERROR:
        logger.error(logging_string)


def test_logging_default_level(logging_fx):
    """
    Test logging level has been set to INFO by default
    """
    logging_fx.setLevel(logging.INFO)
    assert logging_fx.getEffectiveLevel() == logging.INFO


@pytest.mark.parametrize("severity", [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR])
def test_logging_levels(caplog, spooled_logging_fx, random_string_fx, severity):
    """
    Test Console logging with random string to ensure input matches output.
    """
    test_randstring = random_string_fx
    spooled_logging_fx.setLevel(severity)
    log_severity_call(spooled_logging_fx, severity, test_randstring)
    assert caplog.record_tuples == [
        (spooled_logging_fx.name, severity, f"Test String {test_randstring}"),
    ]


@pytest.mark.parametrize("severity", [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR])
def test_logging_to_file_debug(spooled_logging_fx, tmpdir, random_string_fx, severity):
    """
    Test log file input matches written data by logging a random string,
    and then searching that file for the string.

    This test uses a separate file for the string tests, and will not be present in the
    unit_tests.log file.  This change was requested to fix parallel test execution with xdist.
    """
    test_randstring = random_string_fx

    spooled_log = tmpdir.join("searchtest.log")

    fh = logging.FileHandler(spooled_log)
    spooled_logging_fx.addHandler(fh)
    spooled_logging_fx.setLevel(severity)

    log_severity_call(spooled_logging_fx, severity, test_randstring)

    match = 0
    for line in open(spooled_log):
        if test_randstring in line:
            match += 1

    assert match == 1

