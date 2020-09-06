from typing import Optional

import discord
import mongoset
import env
from mongoset.model import DocumentModel, Immutable, ModelTable
import yaml
import validators
from pydantic import validator

if not env.DATABASE:
    db = mongoset.connect(db_name=env.DATABASE_COLLECTION)
else:
    db = mongoset.connect(env.DATABASE, db_name=env.DATABASE_COLLECTION)

with open("admin.yaml") as f:
    admins = yaml.load(f)


class DBUser(DocumentModel):
    discord_id: int = Immutable()
    registered: bool
    registration_step: int
    first_name: Optional[str]
    last_name: Optional[str]
    choate_email: Optional[str]

    @validator("choate_email")
    def validate_email(cls, v):
        if validators.email(v):
            return v
        else:
            raise ValueError("Email validation failed")


class UserTable(ModelTable[DBUser]):
    member_class = DBUser

    def find_discord_user(self, user: discord.User) -> Optional[DBUser]:
        users = self.filter(discord_id=user.id)

        if len(users) == 0:
            return None
        if len(users) == 1:
            return users[0]

        from bot.utils.logger import error

        error(f"More than one user matches the id {user.id}")


user_table = UserTable(db["user"])


def get_db_user(user) -> DBUser:
    db_user = user_table.find_discord_user(user)

    if not db_user:
        db_user = DBUser(discord_id=user.id, registered=False, registration_step=1)
        user_table.create(db_user)

    return db_user


def check_admin(user) -> bool:
    db_user = get_db_user(user)
    if db_user.discord_id in admins:
        return True

    return False
