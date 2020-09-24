import discord
from bot.msgs import templates
import bot.database as db
from bot.register import step1
import re
from bot.utils.logger import info, error
import secrets

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

async def attendance(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info(f"Checking meeting id {client.meeting_id} for {user} who said {message.content}")
    if secrets.compare_digest(message.content, client.meeting_id):
        info(f"Approved meeting id for {user}")
        if db_user.attendance is None:
            db_user.attendance = []
        if client.meeting_id not in db_user.attendance:
            info(f'Added meeting id to {user}')
            db_user.attendance.append(client.meeting_id)
            db.user_table.update(db_user)
            return await user.send(templates.attendance)
        return await user.send(templates.attendance_found)


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

async def start(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info("Validating Admin to Create meeting Code")
    if db_user.discord_id in db.admins: # admin double check
        info("Creating Code")
        meeting_code = secrets.token_hex(4)
        info(f"Code: {meeting_code}")
        await user.send(templates.attendance_set + meeting_code)
        return meeting_code, 'm'

async def end(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info("Validating Admin to end meeting")
    if db_user.discord_id in db.admins:  # admin double check
        info("ending meeting")
        meeting_code = ''
        await user.send(templates.meeting_end)
        return meeting_code, 'm'


### Message routing ###

direct_commands = [(r"help", get_help), (r"info", get_info), (r"register", register), (r"[0-9a-fA-F]{8}", attendance)]  # allows for regex expressions
admin_direct_commands = [(r"email", email), (r"start", start), (r"end", end)]  # allows for regex expressions


async def handle_dm(client, user: discord.User, message: discord.Message):
    responses = []

    for each_command, function in direct_commands:
        if bool(re.fullmatch(each_command, message.content)):
            info(each_command + " command function executed", header=f"[{user}]")
            responses.append(await function(client, user, message))

    if db.check_admin(user):
        for each_command, function in admin_direct_commands:
            if bool(re.fullmatch(each_command, message.content)):
                info(each_command + " command function executed by " + db.get_db_user(user).choate_email + " for " + str(message.content))
                responses.append(await function(client, user, message))

    return responses
