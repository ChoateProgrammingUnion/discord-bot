import discord

from bot.database import user_table, DBUser, get_db_user
from bot.msgs import templates, send


# REGISTRATION STEPS
# 0 - Already registered, is the info correct?  <== Entry point if already registered
# 1 - Prompt for first name                     <== Normal entry point
# 2 - Prompt for last name
# 3 - Prompt email
# 4 - Verify Info
# 5 - Registered!

from bot.utils.logger import info, error


async def handle_join_server(client, user: discord.Member):
    db_user = get_db_user(user)

    info("Added user to database", header=f"[{user}]")

    if db_user.registered:
        db_user.registration_step = 0
        user_table.update(db_user)
        info("User has already registered, setting registration step to 0", header=f"[{user}]")
        await step0(client, user, db_user)
    else:
        db_user.registration_step = 1
        user_table.update(db_user)
        info("User not registered, setting registration step to 1", header=f"[{user}]")
        await step1(user)


async def finish_registration(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient

    client: CPUBotClient

    info("Finishing user registration", header=f"[{user}]")
    db_user.registered = True
    user_table.update(db_user)

    member: discord.Member
    for member in client.guild.members:
        if member.id == user.id:
            break
    else:
        error(f"User not found in guild, cannot complete registration", header=f"[{user}]")
        return

    try:
        await member.edit(nick=f"{db_user.first_name} {db_user.last_name}")
        await member.add_roles(client.club_member_role)
    except discord.Forbidden:
        error("User registered, but bot lacks permission to edit user, are they the server owner?", header=f"[{user}]")

    await welcome_user(client, member)


async def step0(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient

    client: CPUBotClient

    # Create embed
    info_embed = discord.Embed(title="User Info", color=0x0000FF)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)

    # Send message and add reactions
    message = await send(user, templates.welcome_back, embed=info_embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    info("Verification message sent, waiting for user reaction...", header=f"[{user}]")

    # Wait for user reaction
    def check(r: discord.Reaction, u: discord.User):
        return (
            r.message.id == message.id
            and r.emoji in ["👍", "👎"]
            and u.id != client.user.id
        )

    res = await client.wait_for("reaction_add", check=check)
    reaction: discord.reaction = res[0]
    info(f"User reacted with emoji '{reaction.emoji}'", header=f"[{user}]")

    if reaction.emoji == "👍":
        await message.remove_reaction("👍", client.user)
        await message.remove_reaction("👎", client.user)
        db_user.registered = True
        db_user.registration_step = 5
        user_table.update(db_user)
        await step5(client, user, db_user)

    elif reaction.emoji == "👎":
        await message.remove_reaction("👍", client.user)
        await message.remove_reaction("👎", client.user)
        db_user.registered = False
        db_user.registration_step = 1
        user_table.update(db_user)
        await send(user, templates.reset)
        await step1(user, user)


async def step1(user: discord.User, welcome=True):
    if welcome:
        await send(user, templates.new_welcome)
    await send(user, templates.first_name)


async def step1_input(user: discord.User, db_user: DBUser, first_name: str):
    info(f'User provided first name "{first_name}"', header=f"[{user}]")
    db_user.first_name = first_name
    db_user.registration_step = 2
    user_table.update(db_user)
    await step2(user, db_user)


async def step2(user: discord.User, db_user: DBUser):
    await send(user, templates.last_name.format(**locals()))


async def step2_input(user: discord.User, db_user: DBUser, last_name: str):
    info(f'User provided last name "{last_name}"', header=f"[{user}]")
    db_user.last_name = last_name
    db_user.registration_step = 3
    user_table.update(db_user)
    await step3(user, db_user)


async def step3(user: discord.User, db_user: DBUser):
    await send(user, templates.email_address.format(**locals()))


async def step3_input(client, user: discord.User, db_user: DBUser, choate_email: str):
    info(f'User provided Choate email "{choate_email}"', header=f"[{user}]")
    db_user.choate_email = choate_email
    db_user.registration_step = 4
    user_table.update(db_user)
    await step4(client, user, db_user)


async def step4(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient

    client: CPUBotClient

    # Create Embed
    info_embed = discord.Embed(title="User Info", color=0x0000FF)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)

  # Nothing really happened   # Send message and add reactions
    message = await send(user,
        f"""Thanks! Is all of this info correct?""", embed=info_embed
    )
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    info("Verification message sent", header=f"[{user}]")

    # Wait for user reaction
    def check(r: discord.Reaction, u: discord.User):
        return (
            r.message.id == message.id
            and r.emoji in ["👍", "👎"]
            and u.id != client.user.id
        )

    res = await client.wait_for("reaction_add", check=check)
    reaction: discord.reaction = res[0]
    info(f"User reacted with emoji '{reaction.emoji}'", header=f"[{user}]")

    if reaction.emoji == "👍":
        await message.remove_reaction("👍", client.user)
        await message.remove_reaction("👎", client.user)
        db_user.registration_step = 5
        user_table.update(db_user)
        await step5(client, user, db_user)

    elif reaction.emoji == "👎":
        await message.remove_reaction("👍", client.user)
        await message.remove_reaction("👎", client.user)
        await send(user, "Ok, asking for the info again.")
        info("User rejected the info, restarting at step 1", header=f"[{user}]")
        db_user.registration_step = 1
        user_table.update(db_user)
        await step1(user, welcome=False)


async def step5(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient

    client: CPUBotClient

    await finish_registration(client, user, db_user)
    await send(user, templates.finished_registration)
    await send(user, templates.help)


async def handle_dm(client, user: discord.User, message: discord.Message):
    db_user = get_db_user(user)

    if not db_user.registered:
        if db_user.registration_step == 1:
            await step1_input(user, db_user, message.content)
            return True
        elif db_user.registration_step == 2:
            await step2_input(user, db_user, message.content)
            return True
        elif db_user.registration_step == 3:
            await step3_input(client, user, db_user, message.content)
            return True
        elif message.content == "reset":
            db_user.registered = False
            db_user.registration_step = 1
            user_table.update(db_user)
            await step1(user)
            return True

    return False


async def welcome_user(client, member: discord.Member):
    from bot.bot_client import CPUBotClient

    client: CPUBotClient

    await client.new_members_channel.send(templates.public_welcome.format(**locals()))
