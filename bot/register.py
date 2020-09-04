import discord


async def welcome_user(client, member: discord.Member):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    await client.new_members_channel.send(f"Welcome to the server, {member.mention}!")
