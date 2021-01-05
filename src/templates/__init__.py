""" 
{description}

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from uuid import uuid4

from jinja2 import Environment, PackageLoader, select_autoescape
from loguru import logger
import pendulum

from src.commands._list_flags import ListFlags
from src.packages.board import RatBoard
from src.packages.quotation import Quotation
from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.utils.ratlib import Platforms, Status, Colors, color, bold, italic


async def render_rescue(rescue: Rescue, flags: ListFlags):
    template = env.get_template("rescue.jinja2")

    return await template.render_async(rescue=rescue, show_id=flags.show_uuids, flags=flags)


async def render_board(board: RatBoard, **kwargs) -> str:
    template = env.get_template("board.jinja2")
    return await (template.render_async(board=board, **kwargs))


async def render_quotes(rescue: Rescue) -> str:
    template = env.get_template("quotation.jinja2")

    return await template.render_async(rescue=rescue)


logger.debug("loading environment...")

env = Environment(
    loader=PackageLoader("src", "templates"),
    autoescape=select_autoescape(default=False),
    enable_async=True,
)
# inject some objects into the environment so it can be accessed within the templates
env.globals["Colors"] = Colors
env.globals["color"] = color
env.globals["bold"] = bold
env.globals["italic"] = italic
env.globals["Status"] = Status
env.globals["render_rescue"] = render_rescue
env.globals["render_board"] = render_board
env.globals["render_quotes"] = render_quotes
env.globals["Platforms"] = Platforms
env.globals["now"] = pendulum.now
env.globals["tz"] = pendulum.tz
