import unittest
from Modules.Handlers import Commands
import pydle
import asyncio
import Modules.constants as constants
from aiounittest import async_test




class MainTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_run(self):
        raise NotImplementedError("not implemented yet.")


class CommandTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set the bot to something silly, at least its not None. (this won't cut it for proper commands but works here.)
        # as we are not creating commands that do stuff with bot. duh. these are tests after all.
        Commands.bot = "bot"
        super().setUpClass()

    @async_test
    async def test_decorator_single(self):
        """
        Tests if the `Commands.command` decorator can handle string registrations
        """
        alias = ['potato', 'cannon', 'Fodder', "fireball"]
        commands = [f"{Commands.prefix}{name}"for name in alias]
        inChannel = "#unkn0wndev"
        inSender = "unit_tester"
        for command in commands:
            with self.subTest(command=command):
                @Commands.command(command.strip(Commands.prefix))
                async def potato(bot: pydle.Client, channel: str, sender: str):
                    print(f"bot={bot}\tchannel={channel}\tsender={sender}")
                    return bot, channel, sender
                # because commands are normally invoked in an async context we need to actually let it complete
                outBot, outChannel, outSender = await Commands.trigger(message="!potato", sender=inSender,
                                                                   channel=inChannel)
                # otherwise checking for these values is pointless.
                self.assertEqual(inSender, outSender)
                self.assertEqual(inChannel, outChannel)
                self.assertIsNotNone(outBot)
