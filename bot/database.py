import mongoset
import env
from mongoset.model import DocumentModel, Immutable, ModelTable

if not env.DATABASE:
    db = mongoset.connect(db_name="discord-bot")
else:
    db = mongoset.connect(env.DATABASE, db_name="discord-bot")


class User(DocumentModel):
    id: int = Immutable()
    registered: bool = Immutable()
    registration_step: int
    full_name: str
    choate_email: str = Immutable()


class UserTable(ModelTable[User]):
    member_class = User


user_table = UserTable(db["user"])
