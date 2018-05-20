import logging
from datetime import datetime

import config
from Modules.context import Context

LOG = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Quotation(object):
    """
    A quotes object, element of Rescue
    """

    def __init__(self, message: str, author="Mecha",
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                 last_author="Mecha"):
        """
        A Quotation

        Args:
            message (str): quoted message
            author (str): Author of message
            created_at (datetime): time quote first created
            updated_at (datetime): time quote last modified
            last_author (str): last user to modify the quote
        """
        self._message = message
        self._author = author
        self._created_at = created_at
        self._updated_at = updated_at
        self._last_author = last_author

    @property
    def message(self) -> str:
        """
        Recorded message

        Returns:
            str
        """
        return self._message

    @message.setter
    def message(self, value) -> None:
        """
        Sets the recorded message

        Args:
            value (str): message to set

        Returns:
            None:
        """
        if isinstance(value, str):
            self._message = value
        else:
            raise TypeError()

    @property
    def author(self) -> str:
        """
        Original author of quote **READ ONLY**

        Returns:
            str:
        """
        return self._author

    @property
    def created_at(self) -> datetime:
        """
        Whe the quote was first created **READ ONLY**

        Returns:
            datetime:
        """
        return self._created_at

    @property
    def updated_at(self):
        """
        Last time the quote was modified

        Returns:
            datetime: last modify time
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        """
        Set the updated_at property.

        Args:
            value (datetime): last time modified

        Returns:
            None

        Raises:
            TypeError: value given was not a datetime
        """
        if isinstance(value, datetime):
            self._updated_at = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    @property
    def last_author(self) -> str:
        """
        IRC nickname of the last user to modify this quote

        Returns:
            str
        """
        return self._last_author

    @last_author.setter
    def last_author(self, value: str) -> None:
        """
        Sets the last author
        Args:
            value (str): IRC nickname of last modifying user.

        Returns:
            None:

        Raises:
            TypeError: value was not of the correct type.
        """
        if isinstance(value, str):
            self._last_author = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    def modify(self, event_trigger: Context, message: str) -> None:
        """
        Helper method for modifying a quote

        Args:
            event_trigger (Context): Trigger object of invoking user
            message (str): message to set as quoted text

        Returns: None

        """
        self._message = message
        self._updated_at = datetime.utcnow()
        self._last_author = event_trigger.user.username
