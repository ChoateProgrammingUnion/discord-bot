import discord

import bot.channels
import bot.roles
from bot.database import get_db_user
import bot.commands
import bot.register
from env import DISCORD_GUILD_ID
from bot.utils.logger import info, error


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

        await bot.roles.setup_guild_roles(self)
        await bot.channels.setup_guild_channels(self)

    async def on_member_join(self, member: discord.Member):
        if member.guild.id != self.guild.id:
            return

        info(f"{member} has joined the server", header=f"[{member}]")
        await register.handle_join_server(self, member)

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if isinstance(message.author, discord.User):
                if not get_db_user(message.author).registered: # is registered
                    info(f'Received "{message.content}"', header=f"[{message.author}]")
                    await bot.register.handle_dm(self, message.author, message)
                else:
                    await bot.commands.handle_dm(self, message.author, message)
