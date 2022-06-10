import json

from utils.utils import verify_signature, InteractionType
from interactions import ping, command

with open('./env.json') as file:
    env = json.load(file)

def interaction_handler(event, context):
    print(event) # Debug

    json_body = json.loads(event['body'])
    headers = event['headers']

    # Verify Signature
    is_verified = verify_signature(env, event['body'], headers)
    if is_verified:
        if json_body['type'] == int(InteractionType.PING):
            return ping.handler(json_body)
        elif json_body['type'] == int(InteractionType.APPLICATION_COMMAND):
            return command.handler(json_body)
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "content": "Invalid Request Signature",
            }),
        }
