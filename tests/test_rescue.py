"""
test_rescue.py - tests for Rescue and RescueBoard objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

from unittest import TestCase

from Modules.rat_rescue import Rescue
from datetime import datetime


class TestRescue(TestCase):
    """
    Tests for `Modules.Rescue.Rescue`
    """

    @classmethod
    def setUpClass(cls):
        cls.time = datetime.utcnow()

        cls.rescue = Rescue("my-id", "stranded_commander", system="firestone", created_at=cls.time)

    def test_client_property_exists(self):
        """
        Verifies the `Rescue.client` property exists\n
        :return:
        :rtype:
        """
        self.fail()

    def test_client_writeable(self):
        """
        Verifies the `Rescue.client` property can be written to correctly\n
        :return:
        :rtype:
        """
        self.fail()

    def test_created_at_creation(self):
        """
        Verifies the `Rescue.created_at` property was correctly created\n
        :return:
        :rtype:
        """
        self.fail()

    def test_created_at_not_writable(self):
        """
        Verifies the `Rescue.created_at` property cannot be written to\n
        :return:
        :rtype:
        """
        self.fail()

    def test_system_initial_set(self):
        """
        Verifies the `Rescue.system` property was correctly set during init\n
        :return:
        :rtype:
        """
        self.fail()

    def test_system_writable(self):
        self.fail()

