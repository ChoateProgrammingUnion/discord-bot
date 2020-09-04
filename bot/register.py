import discord


async def setup_registration(client, user: discord.User):
    embed = discord.Embed(title="Tile", description="Desc", color=0x00ff00)
    embed.add_field(name="Field", value="Value", inline=False)
    await user.send(embed=embed)


async def welcome_user(client, member: discord.Member):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    await client.new_members_channel.send(f"Welcome to the server, {member.mention}!")
