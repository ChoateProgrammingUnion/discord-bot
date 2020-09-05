import discord
from bot.msgs import templates
import bot.database as db
import re

### Message handling functions ###

async def get_help(client, user: discord.user, message: discord.Message):
    return await user.send(templates.help)

### Message routing ###

direct_commands = [(r"help", get_help)] # allows for regex expressions
admin_direct_commands = [] # allows for regex expressions

async def handle_dm(client, user: discord.User, message: discord.Message):
    responses = []

    for each_command, function in direct_commands:
        if bool(re.fullmatch(each_command, message.content)):
            responses.append(await function(client, user, message))

    if db.check_admin(user):
        for each_command, function in admin_direct_commands:
            if bool(re.fullmatch(each_command, message.content)):
                responses.append(await function(client, user, message))

    return responses


