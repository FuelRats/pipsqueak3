"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from contextlib import contextmanager
from datetime import datetime
from io import StringIO
from typing import Union, Optional, List, TYPE_CHECKING, Dict, Set
from uuid import UUID, uuid4

from dateutil.tz import tzutc
from loguru import logger

from ..epic import Epic
from ..mark_for_deletion import MarkForDeletion
from ..quotation import Quotation
from ..rat import Rat
from ..utils import Platforms, Status, Colors, color, bold

if TYPE_CHECKING:
    from ..board import RatBoard


class Rescue:  # pylint: disable=too-many-public-methods
    """
    A unique rescue
    """

    def __init__(self,  # pylint: disable=too-many-locals
                 uuid: UUID = None,
                 client: Optional[str] = None,
                 system: Optional[str] = None,
                 irc_nickname: Optional[str] = None,
                 board: 'RatBoard' = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 unidentified_rats: Optional[List[str]] = None,
                 active: bool = True,
                 quotes: Optional[List[Quotation]] = None,
                 epic: List[Epic] = None,
                 title: Optional[str] = None,
                 first_limpet: Optional[UUID] = None,
                 board_index: Optional[int] = None,
                 mark_for_deletion: MarkForDeletion = MarkForDeletion(),
                 lang_id: str = "en-US",
                 rats: List[Rat] = None,
                 status: Status = Status.OPEN,
                 code_red=False,
                 platform: Platforms = None):
        """
        creates a rescue

        Args:
            code_red (bool): is the client on emergency oxygen
            status (Status): status attribute for the rescue
            board (RatBoard): RatBoard instance this rescue is attached to, if any.
            uuid (str): API id of rescue
            client (str): Commander name of the Commander rescued
            system (str): System name the Commander is stranded in
                (WILL BE CAST TO UPPER CASE)
            created_at (datetime): time the case was first created
                **( READONLY )**
            updated_at (datetime): last time the case was modified
            unidentified_rats (list): list of unidentified rats responding to
                rescue **(nicknames)**
            active (bool): marks whether the case is active or not
            quotes (list): list of Quotation objects associated with rescue
            epic (bool): is the case marked as an epic
            title (str): name of operation, if applicable
            first_limpet (UUID): Id of the rat that got the first limpet
            board_index (int): index position on the board, if any.
            mark_for_deletion (dict): the markForDeletion object for the API,
                if any.
                - will default to open and not MD'ed
            lang_id (str): language ID of the client, defaults to english.
            irc_nickname (str): clients IRC nickname, may deffer from their
                commander name.
            rats (list): identified Rat(s) assigned to rescue.
            platform(Platforms): Platform for rescue
        """
        self.modified: Set[str] = set()

        self._platform: Platforms = platform
        self.rat_board: 'RatBoard' = board
        self._rats = rats if rats else {}
        self._created_at: datetime = created_at if created_at else datetime.now(tz=tzutc())
        self._updated_at: datetime = updated_at if updated_at else datetime.now(tz=tzutc())
        self._api_id: UUID = uuid if uuid else uuid4()
        self._client: str = client
        self._irc_nick: str = irc_nickname if irc_nickname else client
        self._unidentified_rats = unidentified_rats if unidentified_rats else {}
        self._system: str = system.upper() if system else None
        self._quotes: list = quotes if quotes else []
        self._epic: List[Epic] = epic if epic is not None else []
        self._code_red: bool = code_red
        self._outcome: None = None
        self._title: Union[str, None] = title
        self._first_limpet: UUID = first_limpet
        self._board_index = board_index
        self._mark_for_deletion = mark_for_deletion
        self._board_index = board_index
        self._lang_id = lang_id
        self._status = status
        self._hash = None
        self.active: bool = active

    def __eq__(self, other) -> bool:
        """
        Verify `other` is equal to the self.

        Args:
            other (Rescue): Rescue to compare against

        Returns:
            bool: is equivalent
        """
        if not isinstance(other, Rescue):
            # instance type check
            return NotImplemented
        return other.api_id == self.api_id

    def __hash__(self):

        if self._hash is None:
            self._hash = hash(self.api_id)
        return self._hash

    async def add_rat(self, rat: Rat):
        if rat.unidentified:
            # unidentified rat
            self.unidentified_rats[rat.name.casefold()] = rat

        else:
            self.rats[rat.name.casefold()] = rat

    @property
    def status(self) -> Status:
        """
        Status enum for the rescue

        Returns:
            Status
        """
        return self._status

    @status.setter
    def status(self, value: status):
        """
        Set the value of the status enum

        Args:
            value (Status): new status enum

        Raises:
            TypeError: invalid `value` type
        """
        if isinstance(value, Status):
            self._status = value

            self.modified.add("status")
        else:
            raise TypeError

    @property
    def irc_nickname(self) -> str:
        """
        The client's irc nickname

        Returns:
            str : nickname
        """
        return self._irc_nick

    @irc_nickname.setter
    def irc_nickname(self, value: str) -> None:
        """
        Sets the client's irc nickname

        Args:
            value (str): new nickname

        Raises:
             TypeError : value was not a string.
        """
        if isinstance(value, str):
            self._irc_nick = value

            self.modified.add("irc_nick")
        else:
            raise TypeError

    @property
    def lang_id(self) -> str:
        """
        The language ID the client reported upon entering
        Returns:
            str: clients language ID
        """
        return self._lang_id

    @lang_id.setter
    def lang_id(self, value) -> None:
        """
        Sets the client's language

        Args:
            value (str): new lagnuage code
        """
        if isinstance(value, str):
            self._lang_id = value

            self.modified.add("lang_id")
        else:
            raise TypeError

    @property
    def platform(self):
        """The Rescue's platform"""
        return self._platform

    @platform.setter
    def platform(self, value) -> None:
        """
        Set the client's platform

        Args:
            value (Platforms): new platform
        """
        if isinstance(value, Platforms):
            self._platform = value

            self.modified.add("platform")
        else:
            raise TypeError(f"expected a Platforms, got type {type(value)}")

    @property
    def first_limpet(self) -> UUID:
        """
        The ratID of the rat that got the first limpet

        Returns:
            str : ratid
        """
        return self._first_limpet

    @first_limpet.setter
    def first_limpet(self, value: UUID) -> None:
        """
        Set the value of the first limpet rat

        If the value is not a UUID, this method will attempt to coerce it into one.

        Args:
            value (UUID): rat id of the first-limpet rat.

        Returns:
            None

        Raises:
            ValueError: The value was not a UUID and could not be parsed into a valid one.
        """
        if isinstance(value, UUID):
            self._first_limpet = value

            self.modified.add("first_limpet")
        else:
            # the value wasn't a uuid, but lets try and coerce it into one.
            try:
                # try parse
                guid = UUID(value)
            except (ValueError, AttributeError):
                # the attempt failed
                raise TypeError(f"expected UUID, got type {type(value)}")
            else:
                # the attempt succeeded, lets assign it.
                self._first_limpet = guid

                self.modified.add("first_limpet")

    @property
    def board_index(self) -> int or None:
        """
        The position on the rescue board this rescue holds, if any.

        Returns:
            int: if the board is attached to a case, otherwise None
        """
        return self._board_index

    @board_index.setter
    def board_index(self, value: int or None) -> None:
        """
        Sets the Rescue's board index

        Set to None if the rescue is not attached to the board.

        Args:
            value (int or None): index position

        Returns:
            None
        """
        # negative board indexes should not be possible, right?
        if isinstance(value, int) or value is None:
            if value is None or value >= 0:
                self._board_index = value

                self.modified.add("board_index")
            else:
                raise ValueError("Value must be greater than or equal to zero,"
                                 " or None.")
        else:
            raise TypeError(f"expected int or None, got {type(value)}")

    @property
    def api_id(self) -> UUID:
        """
        The API Id of the rescue.

        Returns: API id

        """

        return self._api_id

    @property
    def client(self) -> str:
        """
        The client associated with the rescue

        Returns:
            (str) the client

        """
        return self._client

    @client.setter
    def client(self, value: str) -> None:
        """
        Sets the client's Commander Name associated with the rescue

        Args:
            value (str): Commander name of the client

        Returns:
            None
        """
        self._client = value

        self.modified.add("client")

    @property
    def created_at(self) -> datetime:
        """
        Case creation time.

        Notes
            this property is **READONLY**.


        It can only be set during Rescue object creation

        Returns:
            datetime: creation date
        """
        return self._created_at

    @property
    def system(self) -> Optional[str]:
        """
        The clients system name

        Returns:
            str: the clients system name
        """
        return self._system

    @system.setter
    def system(self, value: Optional[str]):
        """
        Sets the system property to the upper case of `value`

        Raises:
            AttributeError: if `value` is not a string

        Args:
            value (str): string to set `self.system` to

        Returns:
            None

        Notes:
            this method will cast `value` to upper case, as to comply with
            Fuelrats Api v2.1
        """

        if not (value is None or isinstance(value, str)):
            raise TypeError("value must be of type None or str")

        if value is None:
            # System must be nullable, so we specifically check for it
            self._system = None

            self.modified.add("system")
            return
        # for API v2.1 compatibility reasons we cast to upper case
        self._system = value.upper()

        self.modified.add("system")

    @property
    def active(self) -> bool:
        """
        marker indicating whether a case is active or not. this has no direct
         effect on bot functionality, rather its primary function is case
         management.

        Returns:
            bool: Active state
        """
        return self.status != Status.INACTIVE

    @active.setter
    def active(self, value: bool) -> None:
        """
        setter for `Rescue.active`

        Args:
            value (bool): state to set `active` to.

        Returns:
            None
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.INACTIVE
        else:
            raise ValueError(f"expected bool, got type {type(value)}")

    @property
    def quotes(self) -> List[Quotation]:
        """
        Contains all the quotes associated with this Rescue object.

        Elements of the list are Quotation objects

        Returns:
            list: list of Quotation objects
        """
        return self._quotes

    @quotes.setter
    def quotes(self, value) -> None:
        """
        Sets the value of the quotes property to whatever `value` is.

        This should not be set directly outside of case init, rather via
        `add_quote`

        Args:
            value (list): list of Quotation objects

        Returns:
            None
        """
        if isinstance(value, list):
            self._quotes = value

            self.modified.add("quotes")
        else:
            raise ValueError(f"expected type list, got {type(value)}")

    def add_quote(self, message: str, author: str or None = None) -> None:
        """
        Helper method, adds a `Quotation` object to the list.

        Use this method to add a Quotation to the Rescue

        Args:
            message (str): Message to quote
            author (str): IRC nickname of who is being quoted, if any.
            Otherwise Defaults to Mecha.

        Returns:
            None
        """
        self.modified.add("quotes")
        if author:
            # set the author of the quote
            self.quotes.append(Quotation(author=author, message=message))
        else:
            # otherwise use default
            self.quotes.append(Quotation(message=message))

    @property
    def updated_at(self):
        """
        Last time the rescue object was changed

        Returns:
            datetime
        """

        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        """
        Updates `Rescue.updated_at` property

        Args:
            value (datetime): new last modified datetime

        Raises:
            TypeError: invalid `value` type.
            ValueError: `value` is earlier than creation date.

        Returns:

        """
        if not isinstance(value, datetime):
            raise TypeError(f"Expected datetime, got {type(value)}")
        if value < self.created_at:
            raise ValueError(f"{value} is older than the cases creation date!")
        self._updated_at = value

        self.modified.add("updated_at")

    @property
    def unidentified_rats(self) -> Dict[str, Rat]:
        """
        List of unidentified rats by their IRC nicknames

        Returns:
            list: unidentified rats by IRC nickname
        """
        return self._unidentified_rats

    @unidentified_rats.setter
    def unidentified_rats(self, value) -> None:
        """
        Sets the value of unidentified_rats

        Args:
            value (list): list of strings

        Raises:
            ValueError: value contained illegal types
            TypeError: value was of an illegal type

        """
        if isinstance(value, dict):
            for name, rat in value.items():
                if isinstance(name, str) and isinstance(rat, Rat):
                    self._unidentified_rats[name.casefold()] = rat
                else:
                    raise TypeError(f"Element '{name}' expected to be of type str"
                                    f"str, got {type(name)}")
        else:
            raise TypeError(f"expected type dict, got {type(value)}")

    @property
    def open(self) -> bool:
        """
        Helper method for determining if a case is considered open or not

        Returns:
            bool: is case open?

        """
        return self.status is not Status.CLOSED

    @open.setter
    def open(self, value: bool) -> None:
        """
        helper method for setting the Rescue's open status

        Args:
            value (bool): value to set

        Returns:
            None

        Raises:
            TypeError: value was not a boolean
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.CLOSED
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def epic(self) -> List[Epic]:
        """
        Epic status of the rescue.

        Returns:
            Epic

        Notes:
            This property is **READ ONLY** (for now)
        """
        return self._epic

    @property
    def code_red(self) -> bool:
        """
        Code Red status for the Rescue

        Returns:
            bool
        """
        return self._code_red

    @code_red.setter
    def code_red(self, value: bool):
        if isinstance(value, bool):
            self._code_red = value

            self.modified.add("code_red")
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def outcome(self) -> None:
        """
        Success status for Rescue.

        Returns:
            bool
        """
        return self._outcome

    @property
    def title(self) -> str or None:
        """
        The rescues operation title, if any

        Returns:
            str: operation name if set

            None: no name set.
        """
        return self._title

    @title.setter
    def title(self, value: str or None) -> None:
        """
        Set the operations title.

        Args:
            value (str or None): Operation name.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if value is None or isinstance(value, str):
            self._title = value

            self.modified.add("title")
        else:
            raise TypeError(f"expected type None or str, got {type(value)}")

    @property
    def marked_for_deletion(self) -> MarkForDeletion:
        """
        Mark for deletion object as used by the API

        Returns:
            dict
        """
        return self._mark_for_deletion

    @marked_for_deletion.setter
    def marked_for_deletion(self, value) -> None:
        """
        Sets the Md object

        Args:
            value (MarkForDeletion): value to set the MD object to.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if isinstance(value, MarkForDeletion):
            self._mark_for_deletion = value

            self.modified.add("mark_for_deletion")
        else:
            raise TypeError(f"got {type(value)} expected MarkForDeletion object")

    @property
    def rats(self) -> Dict[str, Rat]:
        """
        Identified rats assigned to rescue

        Returns:
            list: identified rats by UUID
        """
        return self._rats

    @rats.setter
    def rats(self, value):
        """
        Sets the rats property directly, it is recommended to use the helper
        methods to add/remove rats.

        Args:
            value (list): new value for `rats`

        Returns:

        """
        if isinstance(value, dict):
            self._rats = value

            self.modified.add("rats")

        else:
            raise TypeError(f"expected type list got {type(value)}")

    def remove_rat(self, rat: Union[Rat, str]) -> None:
        """
        Removes a rat from the rescue.
        If passed a string: it is treated as a unidentified rat
        If passed a Rat: assume its an identified rat

        Raises:
            KeyError: rat not found

        Args:
            rat: Rat or string unidentified rat name


        """
        if isinstance(rat, Rat):
            # If the rats not there let it burn.
            del self.rats[rat.name.casefold()]

        elif isinstance(rat, str):
            del self.unidentified_rats[rat.casefold()]
        else:
            raise TypeError("expected Union[Rat,str] got type {}", type(rat))

    def mark_delete(self, reporter: str, reason: str) -> None:
        """
        Marks a rescue for deletion

        Args:
            reporter (str): person marking rescue as deleted
            reason (str): reason for the rescue being marked as deleted.

        Raises:
            TypeError: invalid params
        """

        mfd = MarkForDeletion(reporter=reporter, reason=reason, marked=True)
        # both, or neither field, must be set.
        if bool(reporter) ^ bool(reason):
            raise TypeError("both reporter and reason MUST be specified.")

        logger.debug(f"marking rescue @{self.api_id} for deletion. reporter is {reporter} and "
                     f"their reason is '{reason}'.")

        self.marked_for_deletion = mfd

    def unmark_delete(self) -> None:
        """
        helper method for unmarking a rescue for deletion. resets the Md object
        """

        self.marked_for_deletion = MarkForDeletion()

    @contextmanager
    def change(self):
        """
        Convenience method for making safe attribute changes.

        FIXME: currently just ensures rescue.updated_at is updated.

        TODO: replace with Board context manager once its implemented

        TODO: replace current context manager with a dummy once the Board
            context manager is a thing.

        TODO: implement API integration (probably in the board Contextmanager

        Returns:
            contextManager


        Examples:
            ```

            with rescue.change():
                rescue.client = foo

            ```
        """
        yield
        self.updated_at = datetime.now(tz=tzutc())

    # TODO: to/from json
    # TODO: track changes
    # TODO: helper method for adding / editing quotes

    def __format__(self, format_spec):
        """
        'c' gives the thing colour
        'a' gives rat assignments
        '@' gives uuids

        order of format specifiers is NOT sensitive but IS case sensitive!
        """

        coloured = 'c' in format_spec
        show_assigned_rats = 'r' in format_spec
        show_uuid = '@' in format_spec
        show_system = "s" in format_spec

        buffer = StringIO()
        buffer.write(f"[{self.board_index}")

        buffer.write(f"@{self.api_id}] " if show_uuid else '] ')
        buffer.write(F"{self.client}'s case, ")
        if self.irc_nickname != self.client and self.irc_nickname is not None:
            buffer.write(f"IRC Nick: {self.irc_nickname!r}, ")

        if show_system and self.system:
            buffer.write(f"in {self.system!r}, ")

        if self.code_red:
            base = '(CR '
            if coloured:
                buffer.write(bold(color(base, Colors.RED)))
            else:
                buffer.write(base)

        if self.platform:
            base = self.platform.name

            if coloured:
                if self.platform is Platforms.XB:
                    buffer.write(color(base, Colors.GREEN))
                elif self.platform is Platforms.PS:
                    buffer.write(color(base, Colors.LIGHT_BLUE))
                else:
                    buffer.write(base)
            else:
                buffer.write(base)

        if self.code_red:
            buffer.write(')')
        if show_assigned_rats:
            buffer.write(' Assigned Rats:')
            buffer.write(', '.join([rat.name for rat in self.rats.values()]))
            buffer.write("\n Unidentified Rats: ")
            buffer.write(", ".join(self.unidentified_rats))

        # convert buffer back to string, and return that
        return buffer.getvalue()

    def __repr__(self):
        return F"Rescue(" \
               F"uuid={self.api_id!r}, " \
               F"client={self.client!r}, " \
               F"system={self.system!r}, " \
               F"irc_nickname={self.irc_nickname!r}, " \
               F"board={self.rat_board!r}, " \
               F"created_at={self.created_at!r}, " \
               F"updated_at={self.updated_at!r}, " \
               F"unidentified_rats={self.unidentified_rats!r}, " \
               F"active={self.active!r}, " \
               F"quotes={self.quotes!r}, " \
               F"epic={self.epic!r}, " \
               F"title={self.title!r}, " \
               F"first_limpet={self.first_limpet!r}, " \
               F"board_index={self.board_index!r}, " \
               F"mark_for_deletion={self.marked_for_deletion!r}, " \
               F"lang_id={self.lang_id!r}, " \
               F"rats={self.rats!r}, " \
               F"status={self.status!r}, " \
               F"code_red={self.code_red!r}, " \
               F"platform={self.platform!r})"
