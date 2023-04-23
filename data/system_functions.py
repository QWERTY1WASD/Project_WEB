from data import db_session
from data.user import User
from typing import Optional


def register(params: dict) -> User:
    db_sess = db_session.create_session()
    user = User(
        nickname=params['nickname'],
        name=params['name'],
        surname=params['surname'],
        phone=params['phone'],
        telegram_id=params['tg_id']
    )
    user.set_password(params['password'])
    db_sess.add(user)
    db_sess.commit()
    return user


def is_nickname_unique(nickname) -> bool:
    db_sess = db_session.create_session()
    user_with_same_nickname = db_sess.query(User).filter(User.nickname == nickname).first()
    db_sess.commit()
    if user_with_same_nickname is not None:
        return False
    return True


def login(params: dict):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == params['nickname']).first()
    if user and user.check_password(params['password']) and user.telegram_id is None:
        user.telegram_id = params['tg_id']
        db_sess.merge(user)
        db_sess.commit()
        return True
    return False


def get_current_user(tg_id: int) -> Optional[User]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == tg_id).first()
    return user


def logout(user):
    db_sess = db_session.create_session()
    user.telegram_id = None
    db_sess.merge(user)
    db_sess.commit()


def change_selected_companion(tg_id: int, companion: str):
    db_sess = db_session.create_session()
    user = get_current_user(tg_id)
    user.selected_companion = companion
    db_sess.merge(user)
    db_sess.commit()


def get_all_users(tg_id: int) -> list:
    db_sess = db_session.create_session()
    user = get_current_user(tg_id)
    if not user.is_admin:
        return []
    return db_sess.query(User).all()
