from phial import Phial, command, Response, Attachment, g
import os

slackbot = Phial('token-goes-here')


@slackbot.command('ping')
def ping():
    '''Simple command which replies with a message'''
    return "Pong"


@slackbot.command('pong')
def pong():
    '''
    Simple command which replies with a message. Has a mutiline
    docstring.
    '''
    return "Ping"


@slackbot.command('hello <name>')
def hello(name):
    '''Simple command with argument which replies to a message'''
    return Response(text="Hi {0}".format(name), channel=command.channel)


@slackbot.command('hello <name> <from_>')
def hello(name, from_):
    '''Simple command with two arguments which replies to a message'''
    return Response(text="Hi {0}, from {1}".format(name, from_),
                    channel=command.channel)


@slackbot.command('react')
def react():
    '''Simple command that reacts to the original message'''
    return Response(reaction="x",
                    channel=command.channel,
                    original_ts=command.message_ts)


@slackbot.command('upload')
def upload():
    '''Simple command that uploads a set file'''
    project_dir = os.path.dirname(__file__)
    file_path = os.path.join(project_dir, 'phial.png')
    return Attachment(channel=command.channel,
                      filename='example.txt',
                      content=open(file_path, 'rb'))


@slackbot.command('reply')
def reply():
    '''Simple command that replies to the original message in a thread'''
    return Response(text="this is a thread",
                    channel=command.channel,
                    original_ts=command.message_ts)


@slackbot.command('start')
def start():
    '''A command which uses an application global variable'''
    g['variable'] = True
    return "Started"


@slackbot.command('stop')
def stop():
    '''A command which uses an application global variable'''
    g['variable'] = False
    return "Stopped"


@slackbot.command('check')
def check():
    '''A command that reads an application global variable'''
    if g['variable']:
        return "Process Started"
    else:
        return "Process Stopped"


@slackbot.command('caseSensitive', case_sensitive=True)
def case_sensitive():
    '''Simple command which replies with a message'''
    return "You typed caseSensitive"


@slackbot.command('messageWithAttachment')
def get_message_with_attachment():
    '''
        A command that posts a message with a Slack attachment
        Read more: https://api.slack.com/docs/message-attachments
    '''
    attachments = [{
        "title": "Here's the title of the attachment",
        "text": "...and here's the text",
        "footer": "Teeny tiny footer text"
    }]
    return Response(channel=command.channel, attachments=attachments)


@slackbot.fallback_command()
def fallback_command(command):
    return "Thats not a command"


if __name__ == '__main__':
    slackbot.run()
