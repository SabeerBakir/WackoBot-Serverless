import json
from utils.utils import DiscordClient
from interactions.command import commands_dictionary

with open('../env.json') as file:
    env = json.load(file)

discord_client = DiscordClient(
    token=env['TOKEN'],
    app_id=env['CLIENT_ID'],
    guild_id=env['GUILD_ID']
)

for command in commands_dictionary.values():
    if discord_client.has_guild_command(command.manifest):
        print(f'''Command "{command.manifest['name']}" is already installed''')
    else:
        print(f'''Installing Command: "{command.manifest['name']}"''')
        discord_client.install_guild_command(command.manifest)
