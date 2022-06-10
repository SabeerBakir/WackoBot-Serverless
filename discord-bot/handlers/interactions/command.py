import json
from utils.utils import InteractionResponseType

def handler(body):
    command_name = body['data']['name']
    if command_name == 'test':
        return {
            "statusCode": 200,
            "body": json.dumps({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': 'Hello World!',
                },
            })
        }