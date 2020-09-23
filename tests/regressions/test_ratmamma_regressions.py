import pytest

from src.packages.utils import Platforms

from src.packages.context import Context

pytestmark = [pytest.mark.asyncio, pytest.mark.regressions]


async def test_spark_277(bot_fx):
    await bot_fx.board.create_rescue(client="FalsePotato", irc_nickname="FalsePotato")

    payload = "Incoming Client: FalsePotato - System: Avici - Platform: PC - O2: OK - Language: English (en-US)"
    await bot_fx.on_message(channel="#ratchat", user="some_announcer", message=payload)

