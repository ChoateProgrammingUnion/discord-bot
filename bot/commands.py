import discord
from bot.msgs import templates
import bot.database as db
import re
from bot.utils.logger import info, error

### Message handling functions ###


async def get_help(client, user: discord.user, message: discord.Message):
    return await user.send(templates.help)


async def get_info(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info_embed = discord.Embed(title="User Info", color=0x0000FF)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)
    await user.send(embed=info_embed)


### Message routing ###

direct_commands = [(r"help", get_help), (r"info", get_info)]  # allows for regex expressions
admin_direct_commands = []  # allows for regex expressions


async def handle_dm(client, user: discord.User, message: discord.Message):
    responses = []

    for each_command, function in direct_commands:
        if bool(re.fullmatch(each_command, message.content)):
            info(each_command + " command function executed", header=f"[{user}]")
            responses.append(await function(client, user, message))

    if db.check_admin(user):
        for each_command, function in admin_direct_commands:
            if bool(re.fullmatch(each_command, message.content)):
                info(each_command + " command function executed")
                responses.append(await function(client, user, message))

    return responses
