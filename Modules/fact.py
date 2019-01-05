"""
fact.py - Fact Class

Provides a Fact object for the Fact Manager Class.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import datetime


class Fact(object):
    def __init__(self, name=None, lang='en', message=None,
                 aliases=None, author=None, edited=None,
                 editedby=None, mfd=False):
        self._name = name
        self._lang = lang
        self._message = message
        self._aliases = aliases
        self._author = author
        self._editedby = editedby
        self._edited = edited if edited else datetime.datetime.now(datetime.timezone.utc)
        self._mfd = mfd

    @property
    def name(self) -> str:
        """
        Name of fact, ie 'prep'
        Returns: name of fact
        """
        return self._name

    @property
    def lang(self) -> str:
        """
        language code, ie 'en'
        Returns: language of fact.

        This may be may be longer than two, in the case of template facts.
        """
        return self._lang

    @property
    def message(self) -> str:
        """
        Message for fact - the set content.
        Returns: str fact content
        """
        return self._message

    @property
    def aliases(self) -> list:
        """
        Registered Aliases for a command.  They are globally unique.
        Returns: list of aliases for fact
        """
        return self._aliases

    @property
    def author(self) -> str:
        """
        Author of fact.
        Returns: str author of fact.
        """
        return self._author

    @property
    def editedby(self) -> str:
        """
        Last editor of fact. Editor is the the rat who added the fact, if new.
        Returns: str editor of fact.
        """
        return self._editedby

    @property
    def edited(self) -> datetime:
        """
        Datetime stamp for last edit of fact
        Returns: datetime object
        """
        return self._edited

    @property
    def mfd(self) -> bool:
        """
        If Fact is marked for deletion, True/False
        Returns: bool marked for deletion
        """
        return self._mfd

    @name.setter
    def name(self, value: str):
        """
        Sets fact name.
        Args:
            value: str
        Returns: Nothing.
        """
        if not isinstance(value, str):
            raise TypeError("Fact.name must be of string type.")

        self._name = value

    @lang.setter
    def lang(self, value: str):
        """
        Sets fact language ID.
        Args:
            value: str language ID
        Returns: Nothing
        """
        if not isinstance(value, str):
            raise TypeError("Fact.lang must be of string type.")

        self._lang = value

    @message.setter
    def message(self, value: str):
        """
        Sets the returned message for the fact
        Args:
            value: str fact message
        Returns: Nothing
        """

        if not isinstance(value, str):
            raise TypeError("Fact.message must be of string type.")

        self._message = value

    @aliases.setter
    def aliases(self, value: list):
        """
        Sets the list of aliases.  This must be a comma-delimited string for proper conversion
        into a postgreSQL TSVECTOR type.
        Args:
            value: list of aliases

        Returns: Nothing
        """

        if not isinstance(value, list):
            raise TypeError("Fact.aliases must be of list type.")

        self._aliases = value

    @author.setter
    def author(self, value: str):
        """
        Sets the author of the fact.
        Args:
            value: str author of fact.

        Returns: Nothing
        """

        if not isinstance(value, str):
            raise TypeError("Fact.author must be of string type")

        self._author = value

    @editedby.setter
    def editedby(self, value: str):
        """
        Sets the editor of the fact. This is the creator upon initial creation.
        Args:
            value: editor of fact

        Returns: Nothing
        """

        if not isinstance(value, str):
            raise TypeError("Fact.editedby must be of string type")

        self._editedby = value

    @edited.setter
    def edited(self, value: datetime):
        """
        Sets the edited timestamp.  This is a datetime stamp and should not be
        modified willy-nilly.
        Args:
            value: datetime last edit date

        Returns: Nothing
        """

        if not isinstance(value, datetime.datetime):
            raise TypeError("Fact.edited must be of datetime type")

        self._edited = value

    @mfd.setter
    def mfd(self, value: bool):
        """
        Sets the Marked For Deletion flag on this fact.
        Args:
            value: bool 'marked for deletion' flag.

        Returns: Nothing
        """

        if not isinstance(value, bool):
            raise TypeError("Fact.mfd must be of bool type")

        self._mfd = value

    @property
    def complete(self) -> bool:
        """
        Checks that a fact has all the required elements to be added, and returns true.

        We do not check fact.mfd or fact.edited here, as they are forced.  Aliases may be
        omitted if there are none to add, and fact.lang defaults to 'en' if not explicitly set.


        Returns: bool True/False
        """
        return True if self.name and self.lang and self.author \
                       and self.message and self.editedby else False
