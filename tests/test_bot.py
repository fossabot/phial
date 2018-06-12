import unittest
from unittest.mock import MagicMock, mock_open
from phial import (Phial, command, Response, Attachment,
                   MessageAttachment, MessageAttachmentField, g)
import phial.wrappers
import phial.globals
import re
import json
from .helpers import MockTrueFunc


class TestPhialBotIsRunning(unittest.TestCase):
    '''Tests for phial's _is_running function'''

    def test_returns_expected_value(self):
        bot = Phial('test-token')
        self.assertFalse(bot._is_running())


class TestPhialBot(unittest.TestCase):

    def setUp(self):
        self.bot = Phial('test-token')
        self.bot._is_running = MockTrueFunc()

    def tearDown(self):
        self.bot = None
        phial.globals._global_ctx_stack.pop()
        phial.globals._command_ctx_stack.pop()

    def assertCommandInCommands(self, command, case_sensitive=False):
        self.assertTrue(self.bot._build_command_pattern(command,
                                                        case_sensitive)
                        in self.bot.commands)


class TestCommandDecarator(TestPhialBot):
    '''Tests for phial's command decorator'''

    def test_command_decorator_functionality(self):
        @self.bot.command('test')
        def command_function():
            return 'test'

        self.assertCommandInCommands('test')
        self.assertTrue(command_function in self.bot.commands
                        .values())

    def test_command_decorator_calls_add_command(self):
        self.bot.add_command = MagicMock()

        @self.bot.command('test_add_called')
        def test_command_function():
            return 'test'
        self.bot.add_command.assert_called_with('test_add_called',
                                                test_command_function,
                                                False)


class TestAliasDecarator(TestPhialBot):
    '''Tests for phial's alias decorator'''

    def test_command_decorator_functionality(self):
        @self.bot.alias('test')
        def command_function():
            return 'test'

        self.assertCommandInCommands('test')
        self.assertTrue(command_function in self.bot.commands
                        .values())

    def test_command_decorator_calls_add_command_case_insensitive(self):
        self.bot.add_command = MagicMock()

        @self.bot.alias('test_add_called')
        def test_command_function():
            return 'test'
        self.bot.add_command.assert_called_with('test_add_called',
                                                test_command_function,
                                                False)

    def test_command_decorator_calls_add_command_case_sensitive(self):
        self.bot.add_command = MagicMock()

        @self.bot.alias('test_add_called', case_sensitive=True)
        def test_command_function():
            return 'test'
        self.bot.add_command.assert_called_with('test_add_called',
                                                test_command_function,
                                                True)


class TestAddCommand(TestPhialBot):
    '''Tests for phial's add_command function'''

    def test_add_command_functionality(self):
        def command_function():
            return 'test'
        self.bot.add_command('test', command_function)

        self.assertCommandInCommands('test')
        self.assertTrue(command_function in self.bot.commands
                        .values())

    def test_add_command_errors_on_duplicate_name(self):
        def command_function():
            return 'test'

        self.bot.add_command('duplicate', command_function)

        with self.assertRaises(ValueError) as context:
            self.bot.add_command('duplicate', command_function)

        self.assertTrue('already exists' in str(context.exception))


class TestBuildCommandPattern(TestPhialBot):
    '''Test phial's build_command_pattern function'''

    def test_build_command_pattern_no_substition_ignore_case(self):
        command_template = 'test'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          False)
        expected_result = re.compile('^test$', re.IGNORECASE)
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_single_substition_ignore_case(self):
        command_template = 'test <one>'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          False)
        expected_result = re.compile('^test (?P<one>.+)$', re.IGNORECASE)
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_multiple_substition_ignore_case(self):
        command_template = 'test <one> <two>'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          False)
        expected_result = re.compile('^test (?P<one>.+) (?P<two>.+)$',
                                     re.IGNORECASE)
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_no_substition_case_sensitive(self):
        command_template = 'tEst'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          True)
        expected_result = re.compile('^tEst$')
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_single_substition_case_sensitive(self):
        command_template = 'tEst <one>'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          True)
        expected_result = re.compile('^tEst (?P<one>.+)$')
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_multiple_substition_case_sensitive(self):
        command_template = 'tEst <one> <two>'
        command_pattern = self.bot._build_command_pattern(command_template,
                                                          True)
        expected_result = re.compile('^tEst (?P<one>.+) (?P<two>.+)$')
        self.assertTrue(command_pattern == expected_result)


class TestGetCommandMatch(TestPhialBot):
    '''Test phial's get_command_match function'''

    def test_basic_functionality(self):
        self.bot.commands = {re.compile('^test$'): 'test'}
        kwargs, command_pattern = self.bot.get_command_match('!test')
        self.assertTrue(kwargs == {})
        self.assertTrue(command_pattern == re.compile('^test$'))

    def test_single_substition_matching(self):
        self.bot.commands = {re.compile('^test (?P<one>.+)$'): 'test'}
        kwargs, command_pattern = self.bot.get_command_match('!test first')
        self.assertTrue(kwargs == {'one': 'first'})
        self.assertTrue(command_pattern == re.compile('^test (?P<one>.+)$'))

    def test_multi_substition_matching(self):
        self.bot.commands = {re.compile('^test (?P<one>.+) (?P<two>.+)$'):
                             'test'}
        kwargs, command_pattern = self.bot.get_command_match('!test one two')
        self.assertTrue(kwargs == {'one': 'one', 'two': 'two'})
        self.assertTrue(command_pattern ==
                        re.compile('^test (?P<one>.+) (?P<two>.+)$'))

    def test_returns_none_correctly(self):
        command_match = self.bot.get_command_match('test')
        self.assertTrue(command_match is None)


class TestCreateCommand(TestPhialBot):
    '''Test phial's create_command function'''

    def test_basic_functionality(self):
        command_patern = re.compile('^test$')
        self.bot.commands = {command_patern: 'test'}
        command_message = phial.wrappers.Message('!test',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        command = self.bot._create_command(command_message)
        expected_command = phial.wrappers.Command(command_patern,
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  command_message)
        self.assertEquals(command, expected_command)

    def test_basic_functionality_with_args(self):
        command_patern = re.compile('^test (?P<one>.+)$')
        self.bot.commands = {command_patern: 'test'}
        command_message = phial.wrappers.Message('!test first',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        command = self.bot._create_command(command_message)
        expected_command = phial.wrappers.Command(command_patern,
                                                  'channel_id',
                                                  {'one': 'first'},
                                                  'user',
                                                  command_message)
        self.assertEquals(command, expected_command)

    def test_errors_when_no_command_match(self):
        with self.assertRaises(ValueError) as context:
            command_message = phial.wrappers.Message('!test',
                                                     'channel_id',
                                                     'user',
                                                     'timestamp')
            self.bot._create_command(command_message)
        self.assertTrue('Command "test" has not been registered'
                        in str(context.exception))


class TestHandleCommand(TestPhialBot):
    '''Test phial's handle_command function'''

    def test_handle_command_basic_functionality(self):

        test_func = MagicMock()
        self.bot.add_command('test', test_func)
        message = phial.wrappers.Message(text="!test",
                                         channel="channel_id",
                                         user="user",
                                         timestamp="timestamp")
        command_patern = self.bot._build_command_pattern('test', False)
        command_instance = phial.wrappers.Command(command_patern,
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  message)
        self.bot._handle_command(command_instance)

        self.assertTrue(test_func.called)


class TestCommandContextWorksCorrectly(TestPhialBot):

    def test_command_context_works_correctly(self):
        command_pattern = self.bot._build_command_pattern('test', False)

        def test_func():
            self.assertTrue(command.command_pattern == command_pattern)
            self.assertTrue(command.channel == 'channel_id')
            self.assertTrue(command.args == {})

        self.bot.add_command('test', test_func)
        message = phial.wrappers.Message(text="!test",
                                         channel="channel_id",
                                         user="user",
                                         timestamp="timestamp")
        command_instance = phial.wrappers.Command(command_pattern,
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  message)
        self.bot._handle_command(command_instance)

    def test_command_context_pops_correctly(self):
        def test_func():
            pass

        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Message('!test',
                                                  'channel_id',
                                                  'user',
                                                  'timestamp')
        self.bot._handle_message(command_instance)

        with self.assertRaises(RuntimeError) as context:
            print(command)
        self.assertTrue('Not in a context with a command'
                        in str(context.exception))


class TestParseSlackOutput(TestPhialBot):

    def test_basic_functionality(self):
        sample_slack_output = [{
                                'text': '!test',
                                'channel': 'channel_id',
                                'user': 'user_id',
                                'ts': 'timestamp'
                               }]
        command_message = self.bot._parse_slack_output(sample_slack_output)
        expected_command_message = phial.wrappers.Message('!test',
                                                          'channel_id',
                                                          'user_id',
                                                          'timestamp')
        self.assertEquals(command_message, expected_command_message)

    def test_returns_message_correctly_for_normal_message(self):
        sample_slack_output = [{'text': 'test', 'channel': 'channel_id',
                                'user': 'user', 'ts': 'timestamp'}]
        command_message = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(type(command_message) is phial.wrappers.Message)

    def test_returns_none_correctly_if_no_messages(self):
        sample_slack_output = []
        command_message = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(command_message is None)

    def test_returns_message_with_bot_id_correctly(self):
        sample_slack_output = [{
                                'text': '!test',
                                'channel': 'channel_id',
                                'user': 'user_id',
                                'ts': 'timestamp',
                                'bot_id': 'bot_id'
                              }]
        command_message = self.bot._parse_slack_output(sample_slack_output)
        self.assertEqual(command_message.bot_id, 'bot_id')


class TestSendMessage(TestPhialBot):
    '''Test phial's send_message function'''

    def test_send_message(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock(return_value="test")
        message = Response(text='Hi test', channel='channel_id')
        self.bot.send_message(message)

        self.bot.slack_client.api_call.assert_called_with('chat.postMessage',
                                                          channel='channel_id',
                                                          text='Hi test',
                                                          as_user=True,
                                                          attachments='null',
                                                          user=None)

    def test_send_reply(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock(return_value="test")
        message = Response(text='Hi test',
                           channel='channel_id',
                           original_ts='timestamp')
        self.bot.send_message(message)

        self.bot.slack_client.api_call \
            .assert_called_with('chat.postMessage',
                                channel='channel_id',
                                text='Hi test',
                                thread_ts='timestamp',
                                as_user=True,
                                attachments='null',
                                user=None)


class TestSendMessageWithMessageAttachments(TestPhialBot):
    '''Test phial's send_message function with message attachments'''

    def test_send_message(self):
        self.bot.slack_client = MagicMock()
        message = Response(channel="channel_id",
                           attachments=[MessageAttachment(
                                fallback="fallback",
                                author_name="John Doe",
                                author_link="https://example.com/author",
                                author_icon="https://example.com/author.jpg",
                                color="#36a64f",
                                title="Title",
                                title_link="https://example.com",
                                image_url="https://example.com/image.jpg",
                                text="Go to Example Website",
                                footer="Footer text",
                                footer_icon="https://example.com/footer.jpg",
                                thumb_url="https://example.com/thumb.jpg",
                                fields=[
                                    MessageAttachmentField(
                                        title="Established",
                                        value="2008",
                                        short=False),
                                    MessageAttachmentField(
                                        title="Users",
                                        value="27 Million",
                                        short=True)])])
        self.bot.send_message(message)

        attachments = """
        [
            {
                "fallback":"fallback",
                "color":"#36a64f",
                "author_name":"John Doe",
                "author_link":"https://example.com/author",
                "author_icon":"https://example.com/author.jpg",
                "title":"Title",
                "title_link":"https://example.com",
                "text":"Go to Example Website",
                "image_url":"https://example.com/image.jpg",
                "thumb_url":"https://example.com/thumb.jpg",
                "fields":[
                    {
                        "title":"Established",
                        "value":"2008",
                        "short":false
                    },
                    {
                        "title":"Users",
                        "value":"27 Million",
                        "short":true
                    }
                ],
                "footer":"Footer text",
                "footer_icon":"https://example.com/footer.jpg"
            }
        ]
"""
        self.bot.slack_client.api_call.assert_called_with(
                'chat.postMessage',
                channel='channel_id',
                as_user=True,
                attachments=json.dumps(json.loads(attachments)),
                text=None,
                user=None)


class TestSendMessageWithMessageAttachmentsDictionary(TestPhialBot):
    '''Test phial's send_message function with message attachments
       passed in as a dictionary'''

    def test_send_message(self):
        self.bot.slack_client = MagicMock()
        message = Response(channel="channel_id",
                           attachments=[{
                               "fallback": "fallback",
                               "author_name": "John Doe",
                               "author_link": "https://example.com/author",
                               "author_icon": "https://example.com/author.jpg",
                               "color": "#36a64f",
                               "title": "Title",
                               "title_link": "https://example.com",
                               "image_url": "https://example.com/image.jpg",
                               "text": "Go to Example Website",
                               "footer": "Footer text",
                               "footer_icon": "https://example.com/footer.jpg",
                               "thumb_url": "https://example.com/thumb.jpg",
                               "fields": [
                                   {
                                       "title": "Established",
                                       "value": "2008",
                                       "short": False
                                   },
                                   {
                                       "title": "Users",
                                       "value": "27 Million",
                                       "short": True
                                   }
                               ]
                           }])
        self.bot.send_message(message)

        expected_attachments = """
        [
            {
                "fallback":"fallback",
                "author_name":"John Doe",
                "author_link":"https://example.com/author",
                "author_icon":"https://example.com/author.jpg",
                "color":"#36a64f",
                "title":"Title",
                "title_link":"https://example.com",
                "image_url":"https://example.com/image.jpg",
                "text":"Go to Example Website",
                "footer":"Footer text",
                "footer_icon":"https://example.com/footer.jpg",
                "thumb_url":"https://example.com/thumb.jpg",
                "fields":[
                    {
                        "title":"Established",
                        "value":"2008",
                        "short":false
                    },
                    {
                        "title":"Users",
                        "value":"27 Million",
                        "short":true
                    }
                ]
            }
        ]
"""
        self.bot.slack_client.api_call.assert_called_with(
                'chat.postMessage',
                channel='channel_id',
                as_user=True,
                attachments=json.dumps(json.loads(expected_attachments)),
                text=None,
                user=None)


class TestSendEphemeralMessage(TestPhialBot):
    '''Test phial's send_message function when sending an ephemeral message'''

    def test_ephemeral(self):
        self.bot.slack_client = MagicMock()
        message = Response(channel="channel_id",
                           ephemeral=True,
                           text="Test text",
                           user="user_id")
        self.bot.send_message(message)

        self.bot.slack_client.api_call.assert_called_with(
                'chat.postEphemeral',
                channel='channel_id',
                as_user=True,
                attachments='null',
                text='Test text',
                user='user_id')

    def test_ephemeral_defaults_to_false(self):
        self.bot.slack_client = MagicMock()
        message = Response(channel="channel_id",
                           text="Test text")
        self.bot.send_message(message)

        self.bot.slack_client.api_call.assert_called_with(
                'chat.postMessage',
                channel='channel_id',
                as_user=True,
                attachments='null',
                text='Test text',
                user=None)


class TestSendReaction(TestPhialBot):
    '''Test phial's send_message function'''

    def test_basic_functionality(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock()

        response = Response(reaction='x',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot.send_reaction(response)

        self.bot.slack_client.api_call \
            .assert_called_with("reactions.add",
                                channel=response.channel,
                                timestamp=response.original_ts,
                                name=response.reaction,
                                as_user=True)


class TestUploadAttachment(TestPhialBot):
    '''Test phial's upload_attachment function'''

    def test_basic_functionality(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock()

        attachment = Attachment(channel='channel_id',
                                filename='test.txt',
                                content=mock_open())
        self.bot.upload_attachment(attachment)

        self.bot.slack_client.api_call \
            .assert_called_with("files.upload",
                                channels=attachment.channel,
                                filename=attachment.filename,
                                file=attachment.content)


class TestExecuteResponse(TestPhialBot):
    '''Test phial's execute_response function'''

    def test_send_string(self):
        self.bot.send_message = MagicMock()
        message = phial.wrappers.Message(text="!test",
                                         channel="channel_id",
                                         user="user",
                                         timestamp="timestamp")
        command_instance = phial.wrappers.Command(command_pattern="base",
                                                  channel="channel_id",
                                                  args={},
                                                  user="user",
                                                  message=message)
        phial.globals._command_ctx_stack.push(command_instance)
        self.bot._execute_response("string")
        expected_response = Response(text='string', channel='channel_id')
        self.bot.send_message.assert_called_with(expected_response)
        phial.globals._command_ctx_stack.pop()

    def test_send_message(self):
        self.bot.send_message = MagicMock()
        response = Response(text='Hi test', channel='channel_id')
        self.bot._execute_response(response)
        self.bot.send_message.assert_called_with(response)

    def test_send_reply(self):
        self.bot.send_message = MagicMock()
        response = Response(text='Hi test',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot._execute_response(response)
        self.bot.send_message.assert_called_with(response)

    def test_send_reaction(self):
        self.bot.send_reaction = MagicMock()
        response = Response(reaction='x',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot._execute_response(response)
        self.bot.send_reaction.assert_called_with(response)

    def test_upload_attachment(self):
        self.bot.upload_attachment = MagicMock()
        attachment = Attachment(channel='channel_id',
                                filename='test.txt',
                                content=mock_open())
        self.bot._execute_response(attachment)
        self.bot.upload_attachment.assert_called_with(attachment)

    def test_send_message_attachments(self):
        self.bot.send_message = MagicMock()
        response = Response(channel="channel_id",
                            attachments=[MessageAttachment(
                                fallback="fallback",
                                author_name="John Doe",
                                author_link="https://example.com/author",
                                author_icon="https://example.com/author.jpg",
                                color="#36a64f",
                                title="Title",
                                title_link="https://example.com",
                                image_url="https://example.com/image.jpg",
                                text="Go to Example Website",
                                footer="Footer text",
                                footer_icon="https://example.com/footer.jpg",
                                thumb_url="https://example.com/thumb.jpg",
                                fields=[
                                    MessageAttachmentField(
                                        title="Established",
                                        value="2008",
                                        short=False),
                                    MessageAttachmentField(
                                        title="Users",
                                        value="27 Million",
                                        short=True)])])

        self.bot._execute_response(response)
        self.bot.send_message.assert_called_with(response)

    def test_errors_on_invalid_response(self):
        with self.assertRaises(ValueError) as context:
            self.bot._execute_response([])
        error_msg = 'Only Response or Attachment objects can be returned ' \
                    + 'from command functions'
        self.assertTrue(error_msg in str(context.exception))

    def test_errors_with_invalid_attachment(self):
        attachment = Attachment(channel="channel_id",
                                filename="test_file.txt")
        with self.assertRaises(ValueError) as context:
            self.bot._execute_response(attachment)
        error_msg = 'The content field of Attachment objects must be set'
        self.assertTrue(error_msg in str(context.exception))

    def test_errors_with_reaction_and_reply(self):
        response = Response(reaction='x',
                            text='test',
                            channel='channel_id',
                            original_ts='timestamp')

        with self.assertRaises(ValueError) as context:
            self.bot._execute_response(response)

        error_msg = 'Response objects with an original timestamp can ' \
                    + 'only have one of the attributes: Reaction, ' \
                    + 'Text'
        self.assertTrue(error_msg in str(context.exception))


class TestMiddleware(TestPhialBot):
    '''Test phial's middleware'''

    def test_decarator(self):
        @self.bot.middleware()
        def middleware_test(message):
            return message

        self.assertTrue(middleware_test in self.bot.middleware_functions)

    def test_add_function(self):
        def middleware_test(message):
            return message
        self.bot.add_middleware(middleware_test)
        self.assertTrue(middleware_test in self.bot.middleware_functions)

    def test_halts_message_when_none_returned(self):
        middleware_test = MagicMock(return_value=None)
        self.bot.add_middleware(middleware_test)
        test = MagicMock()
        self.bot.add_command('test', test)
        message = phial.wrappers.Message('!test',
                                         'channel_id',
                                         'user',
                                         'timestamp')
        self.bot._handle_message(message)
        middleware_test.assert_called_once_with(message)
        test.assert_not_called()

    def test_passes_on_message_correctly(self):
        message = phial.wrappers.Message('!test',
                                         'channel_id',
                                         'user',
                                         'timestamp')
        middleware_test = MagicMock(return_value=message)
        self.bot.add_middleware(middleware_test)
        test = MagicMock()
        self.bot.add_command('test', test)
        self.bot._handle_message(message)
        middleware_test.assert_called_once_with(message)


class TestHandleMessage(TestPhialBot):
    '''Test the handle_message function'''

    def test_bot_message_does_not_trigger_command(self):
        message = phial.wrappers.Message('!test',
                                         'channel_id',
                                         'user',
                                         'timestamp',
                                         'bot_id')
        test = MagicMock()
        self.bot.add_command('test', test)
        self.bot._handle_message(message)
        test.assert_not_called()


class TestRun(TestPhialBot):
    '''Test phial's run function'''

    def test_basic_functionality(self):
        def test_func():
            pass
        self.bot.add_command('test', test_func)

        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        command_message = phial.wrappers.Message('!test',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        self.bot._parse_slack_output = MagicMock(return_value=command_message)
        test_command = phial.wrappers.Command(re.compile('^test$'),
                                              'channel_id',
                                              {},
                                              'user_id',
                                              command_message)
        self.bot._create_command = MagicMock(return_value=test_command)
        self.bot._handle_command = MagicMock(return_value=None)

        self.bot.run()
        assert self.bot.slack_client.rtm_connect.call_count == 1
        assert self.bot._parse_slack_output.call_count == 1
        self.bot._create_command.assert_called_with(command_message)
        self.bot._handle_command.assert_called_with(test_command)

    def test_errors_with_invalid_token(self):
        with self.assertRaises(ValueError) as context:
            self.bot.run()
        self.assertTrue('Connection failed. Invalid Token or bot ID'
                        in str(context.exception))

    def test_errors_with_invalid_command(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        test_command = phial.wrappers.Message('!test',
                                              'channel_id',
                                              'user_id',
                                              'timestamp')
        self.bot._parse_slack_output = MagicMock(return_value=test_command)

        expected_msg = 'ValueError: Command "test" has not been registered'
        with self.assertLogs(logger='phial.bot', level='ERROR') as cm:
            self.bot.run()

            error = cm.output[0]
            self.assertIn(expected_msg, error)


class TestGlobalContext(unittest.TestCase):

    def test_global_context_in_command(self):
        bot = Phial('test-token')
        command_pattern1 = bot._build_command_pattern('test', False)
        command_pattern2 = bot._build_command_pattern('test2', False)

        def command_function():
            g['test'] = "test value"

        def second_command_function():
            self.assertEquals(g['test'], "test value")

        bot.add_command('test', command_function)
        message = phial.wrappers.Message(text="!test",
                                         channel="channel_id",
                                         user="user",
                                         timestamp="timestamp")
        command_instance = phial.wrappers.Command(command_pattern1,
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  message)
        bot.add_command('test2', second_command_function)
        second_command_instance = phial.wrappers.Command(command_pattern2,
                                                         'channel_id',
                                                         {},
                                                         'user',
                                                         message)
        bot._handle_command(command_instance)
        bot._handle_command(second_command_instance)

    def test_global_context_fails_outside_app_context(self):
        with self.assertRaises(RuntimeError) as context:
            print(g)
        self.assertTrue('Working outside the app context'
                        in str(context.exception))
