import unittest

from Modules import permissions


class PermissionTests(unittest.TestCase):

    def setUp(self):
        super().setUp()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_permission_greater(self):
        """
        Tests if Permission_a > Permission_b functions correctly.
        :return:
        """
        self.assertTrue(permissions.RAT > permissions.RECRUIT)
        self.assertTrue(permissions.ADMIN > permissions.RAT)
        self.assertFalse(permissions.RAT > permissions.TECHRAT)

    def test_permission_lesser(self):
        """
        Tests if Permission_a < Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.RECRUIT < permissions.RAT)
        self.assertTrue(permissions.RAT < permissions.TECHRAT)
        self.assertFalse(permissions.ORANGE < permissions.TECHRAT)

    def test_permission_le(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.ADMIN <= permissions.ADMIN)
        self.assertFalse(permissions.ADMIN <= permissions.RAT)
        self.assertTrue(permissions.ADMIN <= permissions.ORANGE)

    def test_permission_ge(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.ADMIN >= permissions.ADMIN)
        self.assertTrue(permissions.ADMIN >= permissions.RAT)
        self.assertFalse(permissions.ADMIN >= permissions.ORANGE)

    def test_permission_equal(self):
        """
        Verifies that Permission_a == Permission_b
        :return:
        """
        self.assertTrue(permissions.RAT == permissions.RAT)
        self.assertTrue(permissions.TECHRAT == permissions.TECHRAT)
        self.assertTrue(permissions.ADMIN == permissions.NETADMIN)

    def test_permission_not_equal(self):
        """
        Verifies that Permission_a != Permission_b
        :return:
        """
        self.assertTrue(permissions.RAT != permissions.TECHRAT)
        self.assertTrue(permissions.DISPATCH != permissions.ORANGE)
