import secrets
import string

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import String

from app.db.setup import Base


def generate_user_id(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    user_id = "".join(secrets.choice(alphabet) for _ in range(length))
    return user_id


class User(Base):
    __tablename__ = "users"

    id = Column(String(12), primary_key=True, default=generate_user_id)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    patronymic = Column(String(50), nullable=True)
    phone_number = Column(String(11), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True)
    country = Column(String(50), nullable=False)
    data_created = Column(DateTime(), server_default=func.now())
    date_modified = Column(DateTime(), server_default=func.now(), onupdate=func.now())
