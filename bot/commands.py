import discord
from bot.msgs import templates, send, ctf_active, ctf_problems, ctf_flags
import bot.database as db
from bot.register import step1
import re
from bot.utils.logger import info, error
import secrets

""" Message handling functions """


async def get_help(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    if db_user.discord_id in db.admins:
        return await send(user, templates.help + '\n' + templates.admin_help)
    else:
        return await send(user, templates.help)


async def get_info(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    info_embed = discord.Embed(title="User Info", color=0x0000FF)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)
    return await send(user, "", embed=info_embed)


async def register(client, user: discord.user, message: discord.Message):
    db_user = db.get_db_user(user)
    db_user.registered = False
    db_user.registration_step = 1
    db.user_table.update(db_user)
    info("User not registered, setting registration step to 1", header=f"[{user}]")
    return await step1(user)


async def attendance(client, user: discord.user,
                     message: discord.Message):
    # called upon attendance code dm, the attendance code is then added to a list of attended meetings by that user
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


async def ctf_flag_submit(client, user: discord.user,
                          message: discord.Message):  # validates inputted cpuCTF flags
    db_user = db.get_db_user(user)
    info(f"Checking flag for {user} who tried {message.content} who has solved {db_user.ctf_problem_solves}")
    for key in ctf_problems.yaml:
        try:
            if secrets.compare_digest(message.content, ctf_flags.yaml[key].strip()):
                if db_user.ctf_problem_solves is None:
                    db_user.ctf_problem_solves = []
                if key not in db_user.ctf_problem_solves:
                    info(f"Flag {message.content} accepted for {user}")
                    db_user.ctf_problem_solves.append(key)
                    db.user_table.update(db_user)
                    return await user.send(templates.ctf_flag_acceptance)
                else:
                    info(f"Flag {message.content} already accepted for {user}")
                    return await user.send(templates.ctf_flag_already_solved)
        except KeyError:
            pass
    info(f"Flag {message.content} rejected for {user}")
    return await user.send(templates.ctf_flag_rejection)


async def ctf_scoreboard_get(client, user: discord.user,
                             message: discord.Message):  # prints ctf scoreboard
    db_user = db.get_db_user(user)
    scoreboard_formatted = ''
    for place, item in enumerate(client.ctf_scoreboard):
        if f"{db_user.first_name} {db_user.last_name}" in item[0]:
            scoreboard_formatted += f"**{place + 1}. {item[0]}**\n"
        else:
            scoreboard_formatted += f"{place + 1}. {item[0]}\n"
    return await user.send(f"{templates.ctf_scoreboard}\n{scoreboard_formatted}")


async def ctf_get_problems(client, user: discord.user,
                           message: discord.Message):  # prints ctf scoreboard
    db_user = db.get_db_user(user)
    problems_formatted = ''
    for problem in ctf_problems.yaml:
        solved = "solved" if problem in db_user.ctf_problem_solves else "unsolved"
        problems_formatted += f"{problem}: {ctf_problems.yaml[problem].strip()} | {solved}\n"

    return await user.send(f"{templates.ctf_problems}\n{problems_formatted}")

""" Admin commands """


async def email(client, user: discord.user,
                message: discord.Message):  # sends all choate email addresses for the purposes of a mailing list
    db_user = db.get_db_user(user)
    info("Iterating over each user to get each email")
    if db_user.discord_id in db.admins:  # admin double check
        emails = []
        for each_user in db.user_table.all():
            if each_user.choate_email:
                emails.append(each_user.choate_email)

    info("Sending email list")
    return await send(user, "\n".join(emails))


async def start(client, user: discord.user,
                message: discord.Message):  # begins meeting by generating attendance code and setting it to be active
    db_user = db.get_db_user(user)
    info("Validating Admin to Create meeting Code")
    if db_user.discord_id in db.admins:  # admin double check
        info("Checking for existing code")
        if not client.meeting_id:
            info("Creating Code")
            meeting_code = secrets.token_hex(4)
            info(f"Code: {meeting_code}")
            await user.send(templates.attendance_set + meeting_code)
            return meeting_code, 'm'
        else:
            return await user.send(
                f'{templates.attendance_set_failed} Here is the current meeting code: {client.meeting_id}')


async def end(client, user: discord.user,
              message: discord.Message):  # ends meeting by setting the meeting code to an empty string
    db_user = db.get_db_user(user)
    info("Validating Admin to end meeting")
    if db_user.discord_id in db.admins:  # admin double check
        info("ending meeting")
        meeting_code = ''
        await user.send(templates.meeting_end)
        return meeting_code, 'm'


async def get_attendance(client, user: discord.user,
                         message: discord.Message):  # sends attendance for each user who has an attendance entry
    db_user = db.get_db_user(user)
    info("Iterating over each user to get each attendance")
    if db_user.discord_id in db.admins:  # admin double check
        attendances = []
        for each_user in db.user_table.all():
            if each_user.attendance and each_user.choate_email:
                attendances.append(f'{each_user.choate_email} | {len(each_user.attendance)}')

    info("Sending Attendances")
    return await user.send("\n".join(attendances))


async def ctf_get_solves(client, user: discord.user,
                         message: discord.Message):  # ctf: debugging tool to check who solved what problems
    db_user = db.get_db_user(user)
    info("Iterating over each user to get all solves")
    if db_user.discord_id in db.admins:  # admin double check
        solves = []
        for each_user in db.user_table.all():
            if each_user.ctf_problem_solves and each_user.choate_email:
                solves.append(f'{each_user.choate_email} | {len(each_user.ctf_problem_solves)}')

    info("Sending Solves")
    return await user.send("\n".join(solves))


async def ctf_clear_solves(client, user: discord.user,
                           message: discord.Message):  # ctf: tool to clear all solves in the system
    db_user = db.get_db_user(user)
    info("Iterating over each user to clear all solves")
    if db_user.discord_id in db.admins:  # admin double check
        for each_user in db.user_table.all():
            if each_user.ctf_problem_solves:
                each_user.ctf_problem_solves = []
                db.user_table.update(each_user)

    return await ctf_scoreboard_update(client, user, message)


async def ctf_scoreboard_update(client, user: discord.user,
                                message: discord.Message):
    db_user = db.get_db_user(user)
    if db_user.discord_id in db.admins:  # admin double check
        problem_solves = {}
        info("Iterating over each problem for setup")
        for item in ctf_problems.yaml:
            problem_solves[item] = 0
        info("Iterating over each user to get all solves")
        for each_user in db.user_table.all():
            if each_user.ctf_problem_solves:
                for item in problem_solves:
                    if item in each_user.ctf_problem_solves:
                        problem_solves[item] += 1
        info("Iterating over each user to setup scoreboard")
        client.ctf_scoreboard = []
        for each_user in db.user_table.all():
            if each_user.ctf_problem_solves and each_user.first_name and each_user.last_name:
                user_points = 0
                for problem in each_user.ctf_problem_solves:
                    if problem_solves[problem]:
                        user_points += round(client.ctf_point_value / problem_solves[problem])
                client.ctf_scoreboard.append(
                    (f"{each_user.first_name} {each_user.last_name}: {user_points} points", user_points))
        client.ctf_scoreboard = sorted(client.ctf_scoreboard, key=lambda x: x[1], reverse=True)
    return await ctf_scoreboard_get(client, user, message)

async def past_attendance_clear(client, user: discord.user,
                                message: discord.Message):
    db_user = db.get_db_user(user)
    info("Iterating over each user to clear past attendance")
    if db_user.discord_id in db.admins:  # admin double check
        for each_user in db.user_table.all():
            if each_user.choate_email == "mfan21@choate.edu":
                target_attendance = each_user.attendance
        for each_user in db.user_table.all():
            each_user.attendance = [x for x in each_user.attendance if x not in target_attendance]
            db.user_table.update(each_user)
    return await user.send("\n".join(target_attendance))

""" Message routing """

direct_commands = [(r"(?i)help", get_help),
                   (r"(?i)info", get_info),
                   (r"(?i)register", register),
                   (r"[0-9a-fA-F]{8}", attendance),
                   (r"cpuCTF{.+}", ctf_flag_submit),
                   (r"(?i)ctf-scoreboard", ctf_scoreboard_get),
                   (r"(?i)ctf-problems", ctf_get_problems),
                   ]  # allows for regex expressions
admin_direct_commands = [(r"(?i)email", email),
                         (r"(?i)start", start),
                         (r"(?i)end", end),
                         (r"(?i)get-attendance", get_attendance),
                         (r"(?i)ctf-get-solves", ctf_get_solves),
                         (r"(?i)ctf-clear-solves", ctf_clear_solves),
                         (r"(?i)ctf-scoreboard-update", ctf_scoreboard_update),
                         (r"(?i)clear-past-attendance", past_attendance_clear),
                         ]  # allows for regex expressions


async def handle_dm(client, user: discord.User, message: discord.Message):
    responses = []

    for each_command, function in direct_commands:
        if bool(re.fullmatch(each_command, message.content)):
            info(each_command + " command function executed", header=f"[{user}]")
            responses.append(await function(client, user, message))

    if db.check_admin(user):
        for each_command, function in admin_direct_commands:
            if bool(re.fullmatch(each_command, message.content)):
                info(
                    each_command + " command function executed by " + db.get_db_user(user).choate_email + " for " + str(
                        message.content))
                responses.append(await function(client, user, message))

    return responses
