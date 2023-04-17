import sqlalchemy as sa
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname = sa.Column(sa.String, unique=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    name = sa.Column(sa.String, nullable=True)
    surname = sa.Column(sa.String, nullable=True)
    phone = sa.Column(sa.String, nullable=True)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now)
    telegram_id = sa.Column(sa.Integer, unique=True)
    selected_companion = sa.Column(sa.String, nullable=True, default='FlaRakRad')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'<User>: {self.surname} {self.name}, ' \
               f'"{self.nickname}" has phone: {self.phone}, tg_id: {self.telegram_id}, ' \
               f'selected companion: {self.selected_companion}, created date: {self.created_date}'

    @property
    def fio(self) -> str:
        return f'{self.surname} {self.name}'

    @property
    def is_admin(self) -> bool:
        return self.id == 1
