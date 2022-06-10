import json
from utils import DiscordClient

with open('../env.json') as file:
    env = json.load(file)

TEST_COMMAND = {
    'name': 'test',
    'description': 'Basic guild command',
    'type': 1,
}

discord_client = DiscordClient(
    token=env['TOKEN'],
    app_id=env['CLIENT_ID'],
    guild_id=env['GUILD_ID']
)

response = discord_client.has_guild_command(TEST_COMMAND)

print(json.dumps(response.json(), indent=2))