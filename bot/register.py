import discord

from bot.database import user_table, DBUser


# REGISTRATION STEPS
# 0 - Already registered, is the info correct?  <== Entry point if already registered
# 1 - Prompt for first name                     <== Normal entry point
# 1 - Prompt for last name
# 2 - Prompt email
# 3 - Verify Info
# 4 - Registered!

from bot.utils.logger import info


def get_db_user(user) -> DBUser:
    db_user = user_table.find_discord_user(user)

    if not db_user:
        db_user = DBUser(discord_id=user.id, registered=False, registration_step=1)
        user_table.create(db_user)

    return db_user


async def handle_join_server(client, user: discord.Member):
    db_user = get_db_user(user)

    info("Added user to database", header=f"[{user}]")

    db_user.registration_step = 1

    if db_user.registered:
        db_user.registration_step = 0
        info("User has already registered, setting registration step to 0", header=f"[{user}]")

    await step0(client, user, db_user)

    user_table.update(db_user)


async def step0(client, user: discord.User, db_user: DBUser):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    # Create embed
    info_embed = discord.Embed(title="User Info", color=0x0000ff)
    info_embed.add_field(name="__First Name__", value=db_user.first_name)
    info_embed.add_field(name="__Last Name__", value=db_user.last_name)
    info_embed.add_field(name="__Choate Email__", value=db_user.choate_email)

    # Send message and add reactions
    message = await user.send("""**Welcome to the CPU discord server!** It seems you have joined the server on this \
account before, and your previous info was saved. Is this info still correct?""", embed=info_embed)
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
        db_user.registered = True
        db_user.registration_step = 4
        user_table.update(db_user)

    elif reaction.emoji == '👎':
        await message.remove_reaction('👍', client.user)
        await message.remove_reaction('👎', client.user)
        db_user.registration_step = 1
        user_table.update(db_user)
        await user.send("Okay, your account was reset.\n\n")
        await step1(user)


async def step1(user: discord.User):
    await user.send("""\n\n**Welcome to the CPU discord server!** Before you can gain access to the server, we need to \
collect some information about you to make sure you are a Choate student, and so we can add you to our email list.\n\
The first thing we need is your real name so we can change your nickname in the server.\n\
Please type your first name:""")


async def step1_input(user: discord.User, db_user: DBUser, first_name: str):
    db_user.first_name = first_name
    db_user.registration_step = 2
    user_table.update(db_user)
    await step2(user, db_user)


async def step2(user: discord.User, db_user: DBUser):
    await user.send(f"""Thanks, {db_user.first_name}! Next, we'll need your last name.\n\
Please type your last name:""")


async def handle_dm(client, user: discord.User, message: discord.Message):
    db_user = get_db_user(user)

    if db_user.registration_step == 1:
        await step1_input(user, db_user, message.content)


async def welcome_user(client, member: discord.Member):
    from bot.bot_client import CPUBotClient
    client: CPUBotClient

    await client.new_members_channel.send(f"Welcome to the server, {member.mention}!")
