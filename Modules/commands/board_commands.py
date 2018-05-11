"""
board_commands.py - Commands for board manipulation

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from Modules.rat_command import *
from Modules.permissions import *
from Modules.rat_rescue import *
from Modules.database_manager import *
from Modules.rat_board import RatBoard
from ratlib.names import strip_name
import uuid

log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")
board = RatBoard()


def __get_rescue(input: str):
    if str(input).isnumeric():
        rescue: Rescue = board.find_by_index(int(input))
    elif str(input).startswith("@"):
        rescue: Rescue = board.find_by_uuid(uuid.UUID(input[:1]))
    else:
        rescue: Rescue = board.find_by_name(input)
    return rescue


@require_permission(RAT)  # RAT or DISPATCH?
@Commands.command("!go", "!go-.?.?", "!assign", "!assign-.?.?")  # is there RegEx support?
def cmd_go(bot, trigger: Trigger) -> str:
    """
    :param bot: Bot instance
    :param trigger: trigger object
    :type trigger: Trigger
    :param words:
    :param remainder:
    Adds all given Rats to the given case, replies with an localized response.
    :returns
    """
    words = trigger.words
    lang = str(words[0]).replace("go-", "").replace("assign-", "")
    if lang.startswith("go") or lang.startswith("assign"):
        lang = "en"
    rescue: Rescue = __get_rescue(words[1])
    rats = words[2:]
    invalid_rat_names = []

    with rescue.change():
        for ratName in words[2:]:
            rat_to_add = Rats.get_rat(name=strip_name(ratName), platform=rescue.platform)
            if not rat_to_add:
                invalid_rat_names.append(ratName)
                rescue.unidentified_rats.append(ratName)

    result = DataBaseManager.get_fact("go", lang)

    trigger.reply(f"{rescue.irc_nickname}:" + result.format(rats=rats))
    if len(invalid_rat_names) > 0:
        trigger.reply(
            f"{trigger.nickname} The following Rats are NOT registered on the Platform: " +
            ", ".join(invalid_rat_names)
        )
        return "not registered"
    return "ok"


@require_permission(RAT)
@Commands.command("!clear", "!close")
def cmd_clear(bot, trigger: Trigger, words, *remainder) -> str:
    rescue: Rescue = __get_rescue(words[1])

    if not rescue:
        trigger.reply(f"{trigger.nickname}: Rescue \" {words[1]} \" not found")
        return "rescue not found"
    with rescue.change():
        rescue.is_open = False
        rescue.successful = True

    trigger.reply(f"{trigger.nickname}: Case {rescue.client} has been closed!")
    return "ok"


@require_permission(RAT)
@Commands.command("!cr", "!codered", "!casered")
def cmd_cr(bot, trigger: Trigger, words, *remainder) -> str:
    rescue: Rescue = __get_rescue(words[1])
    if not rescue:
        trigger.reply(f"{trigger.nickname}: Rescue \"{words[1]}\" not found")
        return "rescue not found"

    with rescue.change():
        rescue.code_red = not rescue.code_red
    return "ok"


@require_permission(RAT)
@Commands.command("!active", "!inactive")
def cmd_active(bot, trigger: Trigger, words, *remainder) -> str:
    rescue: Rescue = __get_rescue(words[1])
    if not rescue:
        trigger.reply(f"{trigger.nickname}: Rescue \"{words[1]}\" not found")
        return "rescue not found"
    with rescue.change():
        rescue.active = not rescue.active
    return "ok"


@require_permission(RAT)
@Commands.command("!md")
def cmd_md(bot, trigger: Trigger, words, *remainder) -> str:
    rescue: Rescue = __get_rescue(words[1])
    if not rescue:
        trigger.reply(f"{trigger.nickname}: Rescue \"{words[1]}\" not found")
        return "rescue not found"
    with rescue.change():
        rescue.is_open = False
        rescue.mark_for_deletion = {
            "marked": True,
            "reason": words[2:],
            "reporter": trigger.nickname
        }
    return "ok"


@require_permission(OVERSEER)
@Commands.command("!mdremove")
def cmd_mdremove(bot, trigger: Trigger, words, *remainder) -> str:
    if words[1][0] != '@':
        trigger.reply(f"{trigger.nickname}: Please specify the API-ID")
        return "not api id"
    rescue: Rescue = __get_rescue(words[1])
    if not rescue:
        trigger.reply(f"{trigger.nickname}: Rescue \"{words[1]}\" not found")
        return "rescue not found"
    if not rescue.mark_for_deletion["marked"]:
        trigger.reply(f"{trigger.nickname}: Rescue\"{words[1]}\" is not on the MD-List")
        return "not md-ed"
    with rescue.change():
        rescue.mark_for_deletion = {
            "marked": False,
            "reason": None,
            "reporter": None
        }
    return "ok"


# TODO: add the following commands:
#   !inject / !grab / !sub
#   !list / !quote
#   !sys / !cmdr / !nick
#   !reindex (updateindex, index, ri)
#   !unassign
#   !closed, !recent
#   !reopen / !delete
#   !refreshboard
#   !version
#   !flush, !resetnames
#   !host
#   !nick
#   !quiet
#   !paperworkneeded
#   !invalid
#   ...
# TODO: localization / fact support
