from app import exceptions
from app.models import Group, GroupLogo
from app.utils import localize_subscribers


def get_group(group_id):
    """Получение группы по её ID"""
    group = Group.get_by_id(group_id)
    if group is None:
        raise exceptions.GroupDoesNotExists()
    return group


def create_group(form, user):
    """Создание группы"""
    group = _create_group_from_form(form, user)
    group.subscribers.append(user)
    group.update()

    logo = form.logo.data
    _create_group_logo(logo, group)

    return group


def _create_group_from_form(form, user):
    """Создание группы по данным из формы"""
    group = Group(
        name=form.name.data,
        description=form.description.data,
        admin_id=user.id,
    )
    return group


def _create_group_logo(logo, group):
    """Создание логотипа группы"""
    logo.crop_to_64square()
    GroupLogo.from_raw_image(logo, group)


def on_subscribe_click(group, user):
    """Обработка клика на кнопку подписки на группу.

    Если пользователь подписан на группу, то отписываем от неё.
    Если пользователь не подписанна группу, то подписываем на неё
    """
    if user in group.subscribers:
        group.subscribers.remove(user)
    else:
        group.subscribers.append(user)
    group.update()

    is_subscribed = (user in group.subscribers)
    subscribers_count = len(group.subscribers)
    response_data = {
        "ok": True,
        "isSubscribed": is_subscribed,
        "subscribers": localize_subscribers(subscribers_count),
        "subscribersCount": subscribers_count,
    }
    return response_data
