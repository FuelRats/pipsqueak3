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

from src.packages.board import RatBoard
from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.utils.ratlib import Platforms, Status, Colors, color


async def inject_cases(board: RatBoard):
    snafu = await board.create_rescue(client="snafu", system="somewhere", platform=Platforms.PC)
    snafu.active = False
    fubar = await board.create_rescue(client="fubar", system="Fuelum", platform=Platforms.PC)
    await fubar.add_rat(
        Rat(uuid=None, name="some_unident", platform=Platforms.PC)
    )
    await fubar.add_rat(
        Rat(uuid=None, name="some_other_unidentified", platform=Platforms.PC)
    )

    await snafu.add_rat(Rat(uuid=uuid4(), name="cl4p", platform=Platforms.PC))


def render_rescue(rescue: Rescue, show_id: bool, show_unident: bool):
    template = env.get_template("rescue.jinja2")

    return template.render(rescue=rescue, show_id=show_id, show_unident=show_unident)


def render_board(board: RatBoard, **kwargs) -> str:
    template = env.get_template("board.jinja2")
    return (
        template.render(
            board=board,
            **kwargs
        )
    )


logger.debug("loading environment...")

env = Environment(
    loader=PackageLoader("src", "templates"), autoescape=select_autoescape(default=False)
)
# inject some objects into the environment so it can be accessed within the templates
env.globals['Colors'] = Colors
env.globals['color'] = color
env.globals['Status'] = Status
env.globals['render_rescue'] = render_rescue
env.globals['render_board'] = render_board
