import discord

from bot.database import user_table, DBUser, get_db_user
from bot.msgs import templates


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

    db_user.registration_step = 1

    if db_user.registered:
        db_user.registration_step = 0
        info("User has already registered, setting registration step to 0", header=f"[{user}]")

    await step0(client, user, db_user)

    user_table.update(db_user)


async def finish_registration(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    db_user.registered = True
    user_table.update(db_user)

    member: discord.Member
    for member in client.guild.members:
        if member.id == user.id:
            break
    else:
        error(f"User not found in guild, cannot complete registration")
        return

    await member.edit(nick=f"{db_user.first_name} {db_user.last_name}")
    await member.add_roles(client.club_member_role)
    await welcome_user(client, member)


async def step0(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    # Create embed
    info_embed = discord.Embed(title="User Info", color=0x0000ff)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)

    # Send message and add reactions
    message = await user.send(templates.welcome_back, embed=info_embed)
    await message.add_reaction('👍')
    await message.add_reaction('👎')
    info("Verification message sent, waiting for user reaction...", header=f"[{user}]")

    # Wait for user reaction
    def check(r: discord.Reaction, u: discord.User):
        return r.message.id == message.id and r.emoji in ['👍', '👎'] and u.id != client.user.id
    res = await client.wait_for('reaction_add', check=check)
    reaction: discord.reaction = res[0]
    info(f"User reacted with emoji '{reaction.emoji}'", header=f"[{user}]")

    if reaction.emoji == '👍':
        await message.remove_reaction('👍', client.user)
        await message.remove_reaction('👎', client.user)
        db_user.registered = True
        db_user.registration_step = 5
        user_table.update(db_user)
        await step5(client, user, db_user)

    elif reaction.emoji == '👎':
        await message.remove_reaction('👍', client.user)
        await message.remove_reaction('👎', client.user)
        db_user.registered = False
        db_user.registration_step = 1
        user_table.update(db_user)
        await user.send(templates.reset)
        await step1(user)


async def step1(user: discord.User, welcome=True):
    if welcome:
        await user.send(templates.new_welcome)
    await user.send(templates.first_name)


async def step1_input(user: discord.User, db_user: DBUser, first_name: str):
    db_user.first_name = first_name
    db_user.registration_step = 2
    user_table.update(db_user)
    await step2(user, db_user)


async def step2(user: discord.User, db_user: DBUser):
    await user.send(templates.last_name.format(**locals()))


async def step2_input(user: discord.User, db_user: DBUser, last_name: str):
    db_user.last_name = last_name
    db_user.registration_step = 3
    user_table.update(db_user)
    await step3(user, db_user)


async def step3(user: discord.User, db_user: DBUser):
    await user.send(templates.email_address.format(**locals()))


async def step3_input(client, user: discord.User, db_user: DBUser, choate_email: str):
    db_user.choate_email = choate_email
    db_user.registration_step = 4
    user_table.update(db_user)
    await step4(client, user, db_user)


async def step4(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    # Create Embed
    info_embed = discord.Embed(title="User Info", color=0x0000ff)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)

    # Send message and add reactions
    message = await user.send(f"""Thanks! Is all of this info correct?""", embed=info_embed)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

    # Wait for user reaction
    def check(r: discord.Reaction, u: discord.User):
        return r.message.id == message.id and r.emoji in ['👍', '👎'] and u.id != client.user.id
    res = await client.wait_for('reaction_add', check=check)
    reaction: discord.reaction = res[0]

    if reaction.emoji == '👍':
        await message.remove_reaction('👍', client.user)
        await message.remove_reaction('👎', client.user)
        db_user.registration_step = 5
        user_table.update(db_user)
        await step5(client, user, db_user)

    elif reaction.emoji == '👎':
        await message.remove_reaction('👍', client.user)
        await message.remove_reaction('👎', client.user)
        await user.send("Ok, asking for the info again.")
        db_user.registration_step = 1
        user_table.update(db_user)
        await step1(user, welcome=False)


async def step5(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    await finish_registration(client, user, db_user)
    await user.send(templates.finished_registration)


async def handle_dm(client, user: discord.User, message: discord.Message):
    db_user = get_db_user(user)

    if not db_user.registered:
        if db_user.registration_step == 1:
            await step1_input(user, db_user, message.content)
        elif db_user.registration_step == 2:
            await step2_input(user, db_user, message.content)
        elif db_user.registration_step == 3:
            await step3_input(client, user, db_user, message.content)
        elif message.content == "reset":
            db_user.registered = False
            db_user.registration_step = 1
            user_table.update(db_user)
            await step1(user)


async def welcome_user(client, member: discord.Member):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    await client.new_members_channel.send(templates.public_welcome.format(**locals()))
