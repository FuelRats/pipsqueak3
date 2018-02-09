import unittest
from Modules.Handlers import Commands, CommandNotFoundException
import pydle

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

    def setUp(self):
        # this way command registration between individual tests don't interfere and cause false positives/negatives.
        Commands._flush()
        super().setUp()

    @async_test
    async def test_command_decorator_single(self):
        """
        Tests if the `Commands.command` decorator can handle string registrations
        """
        # bunch of commands to test
        alias = ['potato', 'cannon', 'Fodder', "fireball"]
        commands = [f"{Commands.prefix}{name}"for name in alias]

        for command in commands:
            with self.subTest(command=command):
                @Commands.command(command.strip(Commands.prefix))
                async def potato(bot: pydle.Client, channel: str, sender: str):
                    print(f"bot={bot}\tchannel={channel}\tsender={sender}")
                    return bot, channel, sender
            self.assertIsNotNone(Commands.get_command(command.strip(Commands.prefix)))

    def test_command_decorator_list(self):
        alias = ['potato', 'cannon', 'Fodder', 'fireball']
        trigger_alias = [f"{Commands.prefix}{name}"for name in alias]

        # register the command
        @Commands.command(alias)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in trigger_alias:
            with self.subTest(name=name):
                self.assertIsNotNone(Commands.get_command(name))

    @async_test
    async def test_invalid_command(self):
        """
        Ensures the proper exception is raised when a command is not found.
        :return:
        """
        with self.assertRaises(CommandNotFoundException):
            await Commands.trigger(message="!nope", sender="unit_test", channel="foo")

    def test_find_command(self):
        pass
