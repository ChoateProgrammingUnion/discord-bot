from bot_client import CPUBotClient
from env import DISCORD_TOKEN

def run():
    client = CPUBotClient()
    client.run(DISCORD_TOKEN)
