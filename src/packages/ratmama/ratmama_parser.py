"""
RatMama.py - RatMama and general ratsignal parsing

Provides facilities to parse ratsignals

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import asyncio
import re
from loguru import logger
from typing import Optional, Dict, Any, List
from src.config import CONFIG_MARKER
from io import StringIO
from ..context import Context
from ..rescue import Rescue
from ..rules import rule
from ..user import User
from ..utils import Platforms, color, Colors, bold

import attr


@attr.dataclass
class RatmamaConfig:
    announcer_nicks: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            attr.validators.instance_of(str), attr.validators.instance_of(list)
        )
    )
    """ nicknames that may announce cases """
    trigger_keyword: str = attr.ib(validator=attr.validators.instance_of(str))
    """trigger keyword """

    config_blob: Dict = attr.ib(validator=attr.validators.instance_of(dict))
    """ overall configuration blob """


_config: RatmamaConfig


@CONFIG_MARKER
def rehash_handler(data: Dict):
    """
    Apply new configuration data

    Args:
        data (typing.Dict): new configuration data to apply.

    """
    global _config
    _config = RatmamaConfig(config_blob=data, **data["ratsignal_parser"])


@CONFIG_MARKER
def validate_config(data: Dict):
    # the dataclass does its own validation
    RatmamaConfig(config_blob=data, **data["ratsignal_parser"])


RATMAMA_REGEX = re.compile(
    r"""(?x)
    # The above makes whitespace and comments in the pattern ignored.
    # Saved at https://regex101.com/r/jhKtQD/1
    \s*                                  # Handle any possible leading whitespace
    Incoming\s+Client:\s*                # Match "Incoming Client" prefix
    (?P<all>                             # Wrap the entirety of rest of the pattern
                                         # in a group to make it easier to echo the entire thing
     (?P<cmdr>.+?)                       # Match CDMR name.
     \s+-\s+                             #  -
     System:\s*(?P<system>.*?)           # Match system name
     (?:\s[sS][yY][sS][tT][eE][mM])?     # Strip " system" from end, if present (case insensitive)
     \s+-\s+                             #  -
     Platform:\s*(?P<platform>\w+)       # Match platform (currently can't contain spaces)
     \s+-\s+                             #  -
     O2:\s*(?P<o2>.+?)                   # Match oxygen status
     \s+-\s+                             #  -
     Language:\s*
     (?P<full_language>                  # Match full language text (for regenerating the line)
      (?P<language>.+?)\s*               # Match language name. (currently unused)
      \(                                 # The "(" of "(en-US)"
      (?P<language_code>.+?)             # "en"
      (?:                                # Optional group
       -(?P<language_country>.+)         # "-", "US" (currently unused)
      )?                                 # Actually make the group optional.
      \)                                 # The ")" of "(en-US)"
     )                                   # End of full language text
     (?:                                 # Possibly match IRC nickname
      \s+-\s+                            #  -
      IRC\s+Nickname:\s*(?P<nick>[^\s]+) # IRC nickname
     )?                                  # ... emphasis on "Possibly"
    )                                    # End of the main capture group
    \s*                                  # Handle any possible trailing whitespace
    $                                    # End of pattern
"""
)


@rule(
    r"^Incoming Client:",
    case_sensitive=False,
    full_message=False,
    prefixless=True,
    pass_match=False,
)
async def handle_ratmama_announcement(ctx: Context) -> None:
    """
    Handles the Announcement made by RatMama.
    Details are extracted, wrapped in a Rescue object and appended to the Rescue board.
    An appropriate answer will be sent to IRC.

    Args:
        ctx: Context of the announcement

    Returns: None

    """

    if ctx.user.nickname.casefold() not in (nick.casefold() for nick in _config.announcer_nicks):
        return

    message: str = ctx.words_eol[0]
    result = re.fullmatch(RATMAMA_REGEX, message)
    client_name: str = result.group("cmdr")
    system_name: str = result.group("system")
    platform_name: str = result.group("platform")
    o2_status: bool = result.group("o2") == "OK"  # false is CR
    lang_code: str = f"{result.group('language_code')}-{result.group('language_country').upper()}"
    nickname: Optional[str] = result.group("nick")

    client = await User.from_pydle(ctx.bot, client_name)

    if client is not None and client.hostname in (
        "services.fuelrats.com",
        "bot.fuelrats.com",
    ):
        return await ctx.reply(
            "Signal attempted to create rescue for a service. " "Dispatch: please inject this case."
        )

    exist_rescue: Optional[Rescue] = (
        ctx.bot.board[client_name] if client_name in ctx.bot.board else None
    )

    if exist_rescue:
        # we got a case already!
        await ctx.reply(
            f"{client_name} has reconnected! Case #{exist_rescue.board_index} " f"(RETURN_SIGNAL)"
        )
        # now let's make it more visible if stuff changed
        changed = []
        message = (
            f"Dispatch! Case #{exist_rescue.board_index} {bold('fields changed')} on rejoin,"
            f" please verify:  "
        )
        cr_message = ""
        if (
            (
                exist_rescue.system is not None
                and system_name.casefold() != exist_rescue.system.casefold()
            )
            or exist_rescue.system is None
            and system_name is not None
        ):
            changed.append("system")

        if (
            exist_rescue.platform is None
            or platform_name.casefold() != exist_rescue.platform.name.casefold()
        ):
            changed.append("platform")
        if not o2_status != exist_rescue.code_red:
            cr_message = (
                ", O2 Status!"
                if o2_status
                else f", O2 Status changed, rescue is now {color('CODE RED', Colors.RED)}!"
            )

        if changed:
            # SPARK-46: Warn when a client reconnects with different settings, but differ to dispatch
            # to overwrite existing data instead of doing it ourselves.
            await ctx.reply(f"{message}{', '.join(changed)}{cr_message}")
        return

    platform = None
    if platform_name.casefold() in ("pc", "ps", "xb"):
        platform = Platforms[platform_name.upper()]
    elif platform_name.casefold() == "ps4":
        platform = Platforms.PS
    else:
        logger.warning(f"Got unknown platform from {ctx.user.nickname}: {platform_name}")
    # no case for that name, we have to make our own
    rescue = await ctx.bot.board.create_rescue(
        client=client_name,
        system=system_name,
        irc_nickname=nickname,
        code_red=not o2_status,
        lang_id=lang_code,
        platform=platform,
    )
    platform_signal = f"({rescue.platform.value.upper()}_SIGNAL)" if rescue.platform else ""

    distance_str = "not found in the galaxy DB"
    try:
        system = await asyncio.wait_for(ctx.bot.galaxy.find_system_by_name(system_name), timeout=2)
        if system:
            landmark_info = await asyncio.wait_for(ctx.bot.galaxy.find_nearest_landmark(system), timeout=2)
            if landmark_info:
                landmark, distance = landmark_info
                if system.name != landmark.name:
                    distance_str = f"{distance}ly from {landmark.name}"
                else:
                    distance_str = "landmark"
    except asyncio.TimeoutError:
        distance_str = "galaxy DB request timeout"

    await ctx.reply(
        f"{_config.trigger_keyword.upper()} - CMDR {rescue.client} - "
        f"Reported System: {rescue.system} ({distance_str}) - "
        f"Platform: {rescue.platform.value if rescue.platform else ''} - "
        f"O2: {'NOT OK' if rescue.code_red else 'OK'} - "
        f"Language: {result.group('full_language')}"
        f" (Case #{rescue.board_index}) {platform_signal}"
    )


@rule(
    r"\bdrillsignal\b",
    case_sensitive=False,
    full_message=True,
    pass_match=False,
    prefixless=True,
)
async def handle_ratsignal(ctx: Context) -> None:
    """
    Tries to extract as much details as possible from a self-issued ratsignal and appends
    these details to the rescue board.

    Should it be unable to extract the details, it will open a case and ask for the details
    to be set and will only set the name and nick fields of the rescue.

    Args:
        ctx: Context of the self-issued ratsignal

    Returns: None

    """

    message: str = ctx.words_eol[0]
    # the ratsignal is nothing we are interested anymore
    message = re.sub("ratsignal", "", message, flags=re.I)

    if ctx.user.nickname.casefold() in ctx.bot.board:
        await ctx.reply(
            f"{ctx.user.nickname}: You already sent a Signal! Please stand by,"
            f" someone will help you soon!"
        )
        return

    sep: Optional[str] = None
    if "," in message:
        sep = ","
    elif ";" in message:
        sep = ";"
    elif "|" in message:
        sep = "|"
    elif "-" in message:
        sep = "-"

    if not sep:
        sep = " "

    system: str = None
    code_red: bool = False
    platform: Platforms = None
    for part in message.split(sep):
        part = part.strip()
        if part.casefold() in ("pc",):
            platform = Platforms["PC"]

        elif part.casefold() in (
            "ps",
            "ps4",
            "playstation",
            "playstation4",
            "playstation 4",
        ):
            platform = Platforms["PS"]

        elif part.casefold() in ("xb", "xb1", "xbox", "xboxone", "xbox one"):
            platform = Platforms["XB"]

        elif "o2" in part.casefold():
            code_red = "o2 ok" not in message.casefold()

        else:
            system = part

    if system and "signal" in system.lower():
        logger.error("erroneous case data generated! falling back to spatch...")
        logger.debug("erroneous system: {!r}", system)
        rescue = await ctx.bot.board.create_rescue(
            irc_nickname=ctx.user.nickname, client=ctx.user.nickname
        )
        await ctx.reply(
            f"Case #{rescue.board_index} created for {ctx.user.nickname!r},"
            f" Dispatch please set details"
        )
        return

    rescue = await ctx.bot.board.create_rescue(
        client=ctx.user.nickname,
        system=system,
        irc_nickname=ctx.user.nickname,
        code_red=code_red,
        platform=platform,
    )
    platform_signal = (
        f"{rescue.platform.name.upper()}_SIGNAL" if rescue.platform else _config.trigger_keyword
    )
    await ctx.reply(
        f"Case created for {rescue.client}"
        f" on {rescue.platform.name if rescue.platform else '<unknown platform>'} in {rescue.system}. "
        f"{'O2 status is okay' if not code_red else 'This is a CR!'} "
        f"- {platform_signal}"  # FIXME signal not rendering...
    )
