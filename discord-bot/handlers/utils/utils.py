# Copied from https://github.com/discord/discord-interactions-js/blob/main/src/index.ts
from enum import IntEnum
import requests
import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# The type of interaction this request is.
class InteractionType(IntEnum):
    # A ping.
    PING = 1

    # A command invocation.
    APPLICATION_COMMAND = 2

    # Usage of a message's component.
    MESSAGE_COMPONENT = 3

    # An interaction sent when an application command option is filled out.
    APPLICATION_COMMAND_AUTOCOMPLETE = 4

    # An interaction sent when a modal is submitted.
    APPLICATION_MODAL_SUBMIT = 5


# The type of response that is being sent.
class InteractionResponseType(IntEnum):
    # Acknowledge a `PING`.
    PONG = 1

    # Respond with a message, showing the user's input.
    CHANNEL_MESSAGE_WITH_SOURCE = 4

    # Acknowledge a command without sending a message, showing the user's input. Requires follow-up.
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5

    # Acknowledge an interaction and edit the original message that contains the component later; the user does not see a loading state.
    DEFERRED_UPDATE_MESSAGE = 6

    # Edit the message the component was attached to.
    UPDATE_MESSAGE = 7

    # Callback for an app to define the results to the user.
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8

    # Respond with a modal.
    APPLICATION_MODAL = 9


# Flags that can be included in an Interaction Response.
class InteractionResponseFlags(IntEnum):
# Show the message only to the user that performed the interaction. Message
# does not persist between sessions.
  EPHEMERAL = 1 << 6


# Client to make requests to Discord API easier
class DiscordClient:
    root_api_url: str = 'https://discord.com/api/v10/'
    token: str
    app_id: str
    guild_id: str

    def __init__(self, token, app_id, guild_id) -> None:
        self.token = token
        self.app_id = app_id
        self.guild_id = guild_id


    # Make request to discord helper
    def discord_request(self, endpoint: str, body:dict=None, method='GET'):

        # append endpoint to root API URL
        url = self.root_api_url + endpoint
        headers = {
            'Authorization': f'Bot {self.token}',
            'Content-Type': 'application/json; charset=UTF-8',
        }

        # Make request
        if method == 'GET':
            response = requests.get(url, headers=headers, json=body)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=body)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=body)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=body)
        else:
            raise ValueError(f'Invalid method: {method}. Has to be "GET", "POST", "PUT" or "DELETE"')

        # throw API errors
        if (response.status_code < 200) or (response.status_code > 299):
            data = response.json()
            print(response.status_code)
            raise Exception(json.dumps(data, indent=2))

        # return original response
        return response


    # Checks for a command and installs if it is not present
    def has_guild_command(self, command: dict) -> bool:
        """Check if a Guild Command is installed

        Args:
            command (dict): Command Manifest

        Raises:
            e: Any Exception

        Returns:
            bool: True if installed, False if not
        """


        # API endpoint to get and post guild commands
        endpoint = f'applications/{self.app_id}/guilds/{self.guild_id}/commands'

        try:
            response = self.discord_request(endpoint, body=None, method='GET')
            data = response.json()

            if data is not None:
                installedNames = [installed_command['name'] for installed_command in data]

                # This is just matching on the name, so it's not good for updates
                # TODO: Add version checking for each command name
                if command['name'] in installedNames:
                    return True
                else:
                    return False
                
        except Exception as e:
            raise e


    # Installs a command
    def install_guild_command(self, command: dict):
        # API endpoint to get and post guild commands
        endpoint = f'applications/{self.app_id}/guilds/{self.guild_id}/commands'
        # install command
        try:
            response = self.discord_request(endpoint, body=command, method='POST')
            return response
        except Exception as e:
            raise e


    # Deletes a command
    def delete_guild_command(self, command_id: str):
        # API endpoint to delete guild commands
        endpoint = f'applications/{self.app_id}/guilds/{self.guild_id}/commands/{command_id}'
        # install command
        try:
            response = self.discord_request(endpoint, body=None, method='DELETE')
            return response
        except Exception as e:
            raise e


    # Lists current guild commands
    def list_guild_commands(self):
        # API endpoint to get and post guild commands
        endpoint = f'applications/{self.app_id}/guilds/{self.guild_id}/commands'

        try:
            response = self.discord_request(endpoint, body=None, method='GET')
            data = response.json()
            return data
        except Exception as e:
            raise e

# Helper for verifying request signature
def verify_signature(env: dict, body: str, headers: dict) -> bool:
    """_summary_
    For checking Discord Signature

    Args:
        env (dict): The environment variables (Tokens, Public Key, etc.)
        body (str): The request body
        headers (dict): The headers of the request (X-Signature-Ed25519, X-Signature-Timestamp, etc.)

    Returns:
        bool: True if Signature is verified, False if other otherwise
    """

    # Your public key can be found on your application in the Developer Portal
    PUBLIC_KEY = env['PUBLIC_KEY']

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    # Validating request as per:
    # https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
    # Sometimes these headers can have be fully lowercase or camel case
    
    if 'x-signature-ed25519' in headers.keys():
        signature = headers['x-signature-ed25519']
    elif 'X-Signature-Ed25519' in headers.keys():
        signature = headers['X-Signature-Ed25519']
    else:
        print('No X-Signature-Ed25519 Header')
        return False

    if 'x-signature-timestamp' in headers.keys():
        timestamp = headers['x-signature-timestamp']
    elif 'X-Signature-Timestamp' in headers.keys():
        timestamp = headers['X-Signature-Timestamp']
    else:
        print('No X-Signature-Timestamp Header')
        return False

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False
