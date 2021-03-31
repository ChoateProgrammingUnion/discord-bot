import discord

from bot import register, commands, channels, roles
from bot.database import get_db_user, user_table
from itertools import zip_longest
from bot.msgs import templates, send
from env import DISCORD_GUILD_ID, BOT
from bot.utils.logger import info, error, warning


class CPUBotClient(discord.Client):
    guild: discord.guild.Guild = None
    club_member_role: discord.Role = None
    new_members_channel: discord.TextChannel = None

    def __init__(self, **options):
        super().__init__(**options)
        self.meeting_id = ''
        self.ctf_scoreboard = []
        self.ctf_point_value = 1000

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

        info("Checking existing guild members...")
        for member in self.guild.members:
            member: discord.Member
            if db_user := user_table.find_discord_user(member):
                if db_user.registered:
                    if self.club_member_role in member.roles:
                        info("Existing member found in db, already has Club Member role", header=f"[{member}]")
                    else:
                        try:
                            await member.add_roles(self.club_member_role)
                        except discord.Forbidden:
                            error("Existing member found in db, but bot lacks permission to give "
                                  "Club Member role to this user.", header=f"[{member}]")
                        else:
                            info("Existing member found in db, bot gave user Club Member role", header=f"[{member}]")
                else:
                    if self.club_member_role in member.roles:
                        warning("Unregistered member found in db, has Club Member role for some reason", header=f"[{member}]")
                    else:
                        info("Unregistered member found in db, doesn't has Club Member role", header=f"[{member}]")
            else:
                info("User not found in db", header=f"[{member}]")

    async def on_member_join(self, member: discord.Member):
        if member.guild.id != self.guild.id:
            return

        info(f"{member} has joined the server", header=f"[{member}]")
        await register.handle_join_server(self, member)

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if isinstance(message.author, discord.User) and not str(message.author) == BOT:
                responses = await commands.handle_dm(self, message.author, message)

                if len(responses) == 0:  # No commands were executed
                    executed = False
                    if not get_db_user(message.author).registered:  # is registered
                        executed = await register.handle_dm(self, message.author, message)

                    if not executed: # Nothing really happened
                        # await message.author.send(templates.help)
                        await commands.send(message.author, templates.help)
                        await message.author.send(templates.help)
                else: # meeting attendance code
                    if type(responses[0]) is tuple: # ask Spencer what's happening here
                        if len(responses[0]) == 2:
                            if responses[0][1] == 'm':
                                info(f"Meeting Code set to {responses[0][0]}")
                                self.meeting_id = responses[0][0]
