from app import exceptions
from app.models import Group, User, UserAvatar
from config import Config


def get_user(username_or_id: str) -> User:
    """Получение пользователя по переданному в запросе значению"""
    if username_or_id.isdecimal():
        user_id = int(username_or_id)
        user = User.get_by_id(user_id)
    else:
        username = username_or_id
        user = User.get_by_username(username)

    if user is None:
        raise exceptions.UserDoesNotExists()

    return user


def get_user_by_username(username):
    """Получение пользователя по его имени"""
    user = User.get_by_username(username)
    if user is None:
        raise exceptions.UserDoesNotExists()
    return user


def authorize_from_form(form) -> User:
    """Авторизация пользователя по форме"""
    username = form.username.data
    password = form.password.data
    try:
        user = get_user(username)
        assert user.check_password(password)
    except exceptions.UserDoesNotExists as e:
        raise exceptions.AuthorizationError from e
    except AssertionError:
        raise exceptions.AuthorizationError("Incorrect username or password")
    else:
        return user


def create_user(form):
    """Создание пользователя"""
    user = _create_user_from_form(form)

    avatar = form.avatar.data
    _create_user_avatar(avatar, user)

    return user


def _create_user_from_form(form):
    """Создание пользователя по данным из формы"""
    user = User.create_and_get(
        username=form.username.data,
        email=form.email.data,
        password_hash=form.password.data,
    )
    return user


def _create_user_avatar(avatar, user):
    """Создание аватарки пользователя"""
    avatar.crop_to_64square()
    UserAvatar.from_raw_image(avatar, user)


def get_user_subscribed_groups(user, page):
    """Получение подписок пользователя по-странично"""
    groups_ids = [group.id for group in user.groups]
    return Group.query.filter(Group.id.in_(groups_ids)).paginate(
        page=page,
        per_page=Config.POSTS_PER_PAGE,
        error_out=False,
    )
