from data import db_session
from data.user import User
from typing import Any, Optional


def register(params: dict) -> str:
    db_sess = db_session.create_session()
    user = User(
        nickname=params['nickname'],
        name=params['name'],
        surname=params['surname'],
        phone=params['phone'],
    )
    user.set_password(params['password'])
    db_sess.add(user)
    db_sess.commit()
    return "Успех. Наслаждайся"


def is_nickname_unique(nickname) -> bool:
    db_sess = db_session.create_session()
    user_with_same_nickname = db_sess.query(User).filter(User.nickname == nickname).first()
    db_sess.commit()
    if user_with_same_nickname is not None:
        return False
    return True


def login(params: dict) -> Optional[User]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == params['nickname']).first()
    if user and user.check_password(params['password']):
        return user
    return
