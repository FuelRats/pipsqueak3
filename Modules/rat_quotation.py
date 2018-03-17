from datetime import datetime

from Modules.trigger import Trigger
import logging
import config
LOG = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Quotation(object):
    """
    A quotes object, element of Rescue
    """

    def __init__(self, message: str, author="Mecha",
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                 last_author="Mecha"):
        """
        Creates a new Quotation object\n
        :param message: recorded message
        :type message: str
        :param author: who wrote the message
        :type author: str
        :param created_at: time the quote was created
        :type created_at: datetime
        :param updated_at: last time the quote was touched
        :type updated_at: datetime
        :param last_author: Last person to touch the quote
        :type last_author: str
        """
        self._message = message
        self._author = author
        self._created_at = created_at
        self._updated_at = updated_at
        self._last_author = last_author

    @property
    def message(self) -> str:
        """
        Recorded message\n
        :return: message
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, value) -> None:
        """
        Sets the message property\n
        :param value: value to set
        :type value: str
        :return: None
        :rtype: None
        """
        self._message = value

    @property
    def author(self) -> str:
        """
        Original author of message ( READ ONLY )\n
        :return: author
        :rtype: str
        """
        return self._author

    @property
    def created_at(self) -> datetime:
        """
        When the case was created\n
        :return: time of creation
        :rtype: datetime
        """
        return self._created_at

    @property
    def updated_at(self):
        """
        When the quote was last modified\n
        :return: modify time
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        if isinstance(value, datetime):
            self._updated_at = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    @property
    def last_author(self):
        """
        IRC nickname of the last person to modify this quote
        :return:
        :rtype:
        """
        return self._last_author

    @last_author.setter
    def last_author(self, value):
        if isinstance(value, str):
            self._last_author = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    def modify(self, event_trigger: Trigger, message: str) -> None:
        """
        Helper method for modifying a quote\n
        Args:
            event_trigger (Trigger): Trigger object of invoking user
            message (str): message to set as quoted text

        Returns: None

        """
        self._message = message
        self._updated_at = datetime.utcnow()
        self._last_author = event_trigger.nickname