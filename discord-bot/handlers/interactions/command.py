import json
import inspect
from utils.utils import InteractionResponseType


class TestCommand:
    manifest = {
        'name': 'test',
        'description': 'Basic guild command',
        'type': 1,
    }

    @staticmethod
    def execute(body):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': 'Hello World!',
                },
            })
        }


# This will get all the objects in the current scope that end with "Command".
# It puts them into a dictionary where the key is the command name and the value is its
# function that will perform the commands actions.
command_list = [ eval(obj) for obj in dir() if obj.endswith('Command') ]
command_dict_items = [ (command.manifest['name'], command) for command in command_list ]
commands_dictionary = { command_name:handler for (command_name,handler) in command_dict_items }

def handler(body):
    command_name = body['data']['name']
    if command_name in commands_dictionary.keys():
        return commands_dictionary[command_name].execute(body)
    else:
        print(f'Unknown Command: {command_name}')
