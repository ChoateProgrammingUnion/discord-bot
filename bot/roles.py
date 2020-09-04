from typing import Optional

import discord
from bot.utils.logger import info


class RoleTemplate:
    name: str
    color: discord.Color

    def __init__(self, name, color):
        self.name = name
        self.color = color

    async def setup(self, client) -> discord.Role:
        from bot_client import CPUBotClient
        client: CPUBotClient

        role = await self._find(client)

        if role is None:
            info(f"{self.name} role not found, creating one now...", header=f"[{self.name}]")
            role = await self._create(client)
            info(f"{self.name} role has been created, you should update its perms", header=f"[{self.name}]")
        else:
            info(f"{self.name} role found, skipping creation", header=f"[{self.name}]")

        return role

    async def _create(self, client, **kwargs) -> discord.Role:
        return await client.guild.create_role(name=self.name, color=self.color, **kwargs)

    async def _find(self, client) -> Optional[discord.Role]:
        from bot_client import CPUBotClient
        client: CPUBotClient

        for role in client.guild.roles:
            if role.name == self.name:
                return role


club_member = RoleTemplate("Club Member", discord.Color.blue())


async def setup_guild_roles(client):
    from bot_client import CPUBotClient
    client: CPUBotClient

    client.club_member_role = await club_member.setup(client)
