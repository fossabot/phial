import unittest
from unittest.mock import MagicMock
from phial.commands import help_command


class TestHelpCommand(unittest.TestCase):
    def test_help_command(self):
        bot = MagicMock()
        bot.config = {}
        command = MagicMock()

        command._help = "Test description"
        bot.commands = {"test_pattern": command}
        bot.command_names = {"test_pattern": "test"}

        expected_help_text = "*test* - Test description\n"

        help_text = help_command(bot)
        self.assertEqual(help_text, expected_help_text)

    def test_help_command_multiple(self):
        bot = MagicMock()
        bot.config = {}
        command = MagicMock()
        command2 = MagicMock()

        command._help = "Test description"
        command2._help = "Test description the second"

        bot.commands = {"test_pattern": command, "test2_pattern": command2}
        bot.command_names = {"test_pattern": "test", "test2_pattern": "test2"}

        expected_help_text = "*test* - Test description\n*test2* - " \
                             + "Test description the second\n"

        help_text = help_command(bot)
        self.assertEqual(help_text, expected_help_text)

    def test_help_command_base_text(self):
        bot = MagicMock()
        command = MagicMock()

        command._help = "Test description"

        bot.commands = {"test_pattern": command}
        bot.command_names = {"test_pattern": "test"}
        bot.config = {'baseHelpText': "Base text"}

        expected_help_text = "Base text\n*test* - Test description\n"

        help_text = help_command(bot)
        self.assertEqual(help_text, expected_help_text)