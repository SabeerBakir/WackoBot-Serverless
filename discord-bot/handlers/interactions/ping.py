import json
from utils.utils import InteractionResponseType

def handler(body):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "type": int(InteractionResponseType.PONG),
        }),
    }
