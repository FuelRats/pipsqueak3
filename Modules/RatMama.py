"""
RatMama.py - RatMama and general ratsignal parsing

Provides Facilities to parse ratsignals

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import re
from Modules.context import Context
from Modules.rules import rule
from typing import Optional, List
import Modules.rat_board
from Modules.rat_rescue import Rescue, Platforms
from Modules.galaxy.galaxy import Galaxy
import logging

LOG = logging.getLogger(f"mecha.{__name__}")
board: Modules.rat_board.RatBoard = Modules.rat_board.RatBoard()

ratmama_regex = re.compile(r"""(?x)
    # The above makes whitespace and comments in the pattern ignored.
    # Saved at https://regex101.com/r/jhKtQD/1
    \s*                                  # Handle any possible leading whitespace
    Incoming\s+Client:\s*                # Match "Incoming Client" prefix
    (?P<all>                             # Wrap the entirety of rest of the pattern 
                                         # in a group to make it easier to echo the entire thing
    (?P<cmdr>[^\s].*?)                   # Match CDMR name.
    \s+-\s+                              #  -
    System:\s*(?P<system>.*?)            # Match system name
    (?:\s[sS][yY][sS][tT][eE][mM]|)      # Strip " system" from end, if present (case insensitive)
    \s+-\s+                              #  -
    Platform:\s*(?P<platform>\w+)        # Match platform (currently can't contain spaces)
    \s+-\s+                              #  -
    O2:\s*(?P<o2>.+?)                    # Match oxygen status
    \s+-\s+                              #  -
    Language:\s*
    (?P<full_language>                   # Match full language text (for regenerating the line)
    (?P<language>.+?)\s*                 # Match language name. (currently unused)
    \(                                   # The "(" of "(en-US)"
    (?P<language_code>.+?)               # "en"
    (?:                                  # Optional group
        -(?P<language_country>.+)        # "-", "US" (currently unused)
    )?                                   # Actually make the group optional.
    \)                                   # The ")" of "(en-US)"
    )                                    # End of full language text
    (?:                                  # Possibly match IRC nickname
    \s+-\s+                              #  -
    IRC\s+Nickname:\s*(?P<nick>[^\s]+)   # IRC nickname
    )?                                   # ... emphasis on "Possibly"
    )                                    # End of the main capture group
    \s*                                  # Handle any possible trailing whitespace
    $                                    # End of pattern
""")


@rule(r"^\s*Incoming Client:", case_sensitive=False, full_message=True, prefixless=True,
      pass_match=False)
async def handle_ratmama_announcement(ctx: Context):
    if ctx.user.nickname.casefold() not in ('ratmama[bot]',):
        return

    message: str = ctx.words_eol[0]
    result = re.fullmatch(ratmama_regex, message)
    client_name: str = result.group("cmdr")
    system_name: str = result.group("system")
    platform_name: str = result.group("platform")
    o2_status: bool = result.group("o2") == "OK"
    lang_code: str = result.group("language_code")
    nickname: Optional[str] = result.group("nick")

    exist_rescue: Rescue = board.find_by_name(client_name)

    if exist_rescue:
        # we got a case already!
        await ctx.reply(f"{client_name} has reconnected! Case #{exist_rescue.board_index}")
        # now let's make it more visible if stuff changed
        diff_response: str = ""
        if system_name.casefold() != exist_rescue.system.casefold():
            diff_response += f"System changed! "

        if platform_name.casefold() != exist_rescue.platform.name.casefold():
            diff_response += "Platform changed! "

        if o2_status != exist_rescue.code_red:
            diff_response += "O2 Status changed" if o2_status else\
                "O2 Status changed, it is now CODE RED"

        if not diff_response == "":
            await ctx.reply(diff_response)

    else:
        platform = None

        if platform_name.casefold() in ("pc", "ps", "xb"):
            platform = Platforms[platform_name.upper()]
        else:
            LOG.warning(f"Got unknown platform from RatMama: {platform_name}")

        # no case for that name, we have to make our own
        rescue: Rescue = Rescue(client=client_name, system=system_name, irc_nickname=nickname,
                                code_red=o2_status, lang_id=lang_code, platform=platform)

        board.append(rescue, overwrite=False)
        index = board.find_by_name(client=client_name).board_index
        await ctx.reply(f"RATSIGNAL - CMDR {client_name} - "
                        f"Reported System: {system_name} (distance to be implemented) - "
                        f"Platform: {platform_name} - "
                        f"O2: {'OK' if o2_status else 'NOT OK'} - "
                        f"Language: {result.group('full_language')}"
                        f" (Case #{index}) ({platform_name.upper()}_SIGNAL)"
                        )


@rule("ratsignal", case_sensitive=False, full_message=False, pass_match=False, prefixless=True)
async def handle_selfissued_ratsignal(ctx: Context):
    message: str = ctx.words_eol[0]
    message = message.replace("ratsignal", "")  # the ratsignal is nothing
                                                # we are interested in anymore

    for rescue in board.rescues.values():
        if rescue.irc_nickname.casefold() == ctx.user.nickname.casefold():
            ctx.reply("You already sent a signal, please be patient while a dispatch is underway")
            return

    sep: chr = None
    if ',' in message:
        sep = ','
    elif ';' in message:
        sep = ';'
    elif '|' in message:
        sep = '|'

    if not sep:
        board.append(Rescue(irc_nickname=ctx.user.nickname, client=ctx.user.nickname))
        index = board.find_by_name(ctx.user.nickname)
        await ctx.reply(f"Case #{index} created for {ctx.user.nickname}, please set details")
        return
    parts: List[str] = message.split(sep)
    system: str
    cr: bool
    platform: Platforms
    for part in parts:
        part = part.strip()
        if part.casefold() in ("pc", "ps", "xb"):
            platform = Platforms[part.upper()]

        elif "o2" in part.casefold():
            cr = (part.casefold() != "o2 ok")

        else:
            system = part

    rescue = Rescue(
        client=ctx.user.nickname,
        system=system,
        irc_nickname=ctx.user.nickname,
        code_red=cr,
        platform=platform
    )
    board.append(rescue)
    await ctx.reply(f"Case created for {ctx.user.nickname}"
                    f" on {platform.name} in {system}. "
                    f"{'O2 status is okay' if not cr else 'This is a CR!'}")
