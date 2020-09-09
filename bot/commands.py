import discord
from bot.msgs import templates
import bot.database as db
from bot.register import step1
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
    return await user.send(embed=info_embed)

async def register(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    db_user.registered = False
    db_user.registration_step = 1
    db.user_table.update(db_user)
    info("User not registered, setting registration step to 1", header=f"[{user}]")
    return await step1(user)

### Admin commands ###

async def email(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info("Iterating over each user to get each email")
    if db_user.discord_id in db.admins: # admin double check
        emails = []
        for each_user in db.user_table.all():
            if each_user.choate_email:
                emails.append(each_user.choate_email)

    info("Sending email list")
    return await user.send("\n".join(emails))

### Message routing ###

direct_commands = [(r"help", get_help), (r"info", get_info), (r"register", register)]  # allows for regex expressions
admin_direct_commands = [(r"email", email)]  # allows for regex expressions


async def handle_dm(client, user: discord.User, message: discord.Message):
    responses = []

    message_str = message.content
    message_str = message_str.lower()

    for each_command, function in direct_commands:
        if bool(re.fullmatch(each_command, message_str)):
            info(each_command + " command function executed", header=f"[{user}]")
            responses.append(await function(client, user, message))

    if db.check_admin(user):
        for each_command, function in admin_direct_commands:
            if bool(re.fullmatch(each_command, message_str)):
                info(each_command + " command function executed by " + db.get_db_user(user).choate_email + " for " + str(message.content))
                responses.append(await function(client, user, message))

    return responses
