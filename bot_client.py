import discord

import channels
import roles
from env import DISCORD_GUILD_ID
from utils.logger import info, error


class CPUBotClient(discord.Client):
    guild: discord.guild.Guild = None
    club_member_role: discord.Role = None
    new_members_channel: discord.TextChannel = None

    async def on_ready(self):
        info("Client connected to discord")

        for guild in self.guilds:
            if guild.id == DISCORD_GUILD_ID:
                self.guild = guild
                break

        if self.guild is None:
            error(f"Guild with id {DISCORD_GUILD_ID} not found")
            exit(-1)

        info(f"Guild with id {DISCORD_GUILD_ID} found, name={self.guild.name}")

        await roles.setup_guild_roles(self)
        await channels.setup_guild_channels(self)

    async def on_member_join(self, member: discord.Member):
        info(f"{member} has joined the server", header=f"[{member}]")
        await self.welcome_user(member)

    async def welcome_user(self, member: discord.Member):
        await self.new_members_channel.send(f"Welcome to the server, {member.mention}!")
