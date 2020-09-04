import mongoset
import env

if not env.DATABASE:
    db = mongoset.connect(db_name="discord-bot")
else:
    db = mongoset.connect(env.DATABASE, db_name="discord-bot")
