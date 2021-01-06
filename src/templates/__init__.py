"""
Rendering templates

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pendulum
from jinja2 import Environment, PackageLoader, select_autoescape
from loguru import logger

from src.packages.board import RatBoard
from src.packages.rescue import Rescue
from src.packages.utils.ratlib import Platforms, Status, Colors, color, bold, italic
from .render_flags import RescueRenderFlags


async def render_rescue(rescue: Rescue, flags: RescueRenderFlags):
    template = template_environment.get_template("rescue.jinja2")

    return await template.render_async(rescue=rescue, show_id=flags.show_uuids, flags=flags)


async def render_board(board: RatBoard, **kwargs) -> str:
    template = template_environment.get_template("board.jinja2")
    return await (template.render_async(board=board, **kwargs))


async def render_quotes(rescue: Rescue) -> str:
    template = template_environment.get_template("quotation.jinja2")

    return await template.render_async(rescue=rescue)


logger.debug("loading environment...")

template_environment = Environment(
    loader=PackageLoader("src", "templates"),
    autoescape=select_autoescape(default=False),
    enable_async=True,
)
# inject some objects into the environment so it can be accessed within the templates
template_environment.globals["Colors"] = Colors
template_environment.globals["color"] = color
template_environment.globals["bold"] = bold
template_environment.globals["italic"] = italic
template_environment.globals["Status"] = Status
template_environment.globals["render_rescue"] = render_rescue
template_environment.globals["render_board"] = render_board
template_environment.globals["render_quotes"] = render_quotes
template_environment.globals["Platforms"] = Platforms
template_environment.globals["now"] = pendulum.now
template_environment.globals["tz"] = pendulum.tz
