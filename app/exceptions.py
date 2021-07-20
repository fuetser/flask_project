class UserDoesNotExists(Exception):
    """Пользователь с данным идентификатором не существует"""


class PostDoesNotExists(Exception):
    """Публикация с данным идентификатором не существует"""


class GroupDoesNotExists(Exception):
    """Группа с данным идентификатором не существует"""


class ImageError(Exception):
    ...


class IncorrectQueryParam(Exception):
    ...


class AuthorizationError(Exception):
    ...


class InvalidSearchQuery(Exception):
    ...


class InvalidRequestArgs(Exception):
    """Неверное значение аргумента в запросе"""
