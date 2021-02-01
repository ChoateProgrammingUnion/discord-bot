import discord

from bot.bot_client import CPUBotClient
from env import DISCORD_TOKEN


def run():
    intents = discord.Intents.default()
    intents.members = True
    client = CPUBotClient(intents=intents)
    client.run(DISCORD_TOKEN)
