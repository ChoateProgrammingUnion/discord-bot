#!/usr/bin/env python
import dataset
from bot.database import user_table, DBUser, get_db_user

db_sql = dataset.connect("sqlite:////home/max/test/db.sqlite3")

print(db_sql.tables)
for x in db_sql["oauth_record"].all():
    if x and x.get("discord_user_id"):
        db_user = DBUser(discord_id = x.get("discord_user_id"), registered=True, registration_step=5, choate_email=x.get("school_email"), first_name = x.get("first_name"), last_name = x.get("last_name"), opt_out_email = x.get("opt_out_email"))
        user_table.create(db_user)
