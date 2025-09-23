from typing import Protocol

import pytest
import pytest_mock

from app import exceptions, models
from app.services import user_service


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, id: int) -> models.User | None: ...

    def get_by_username(self, username: str) -> models.User | None: ...


class FakeUserRepository:
    def get_by_id(self, id: int) -> models.User:
        return models.User(id=id)

    def get_by_username(self, username: str) -> models.User:
        return models.User(username=username)


class FakeEmptyUserRepository:
    def get_by_id(self, id: int) -> None:
        return None

    def get_by_username(self, username: str) -> None:
        return None


@pytest.fixture
def fake_user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_empty_user_repository() -> FakeEmptyUserRepository:
    return FakeEmptyUserRepository()


def test_get_user_by_id(
    fake_user_repository: UserRepositoryProtocol,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("app.services.user_service.User", new=fake_user_repository)
    user = user_service.get_user(username_or_id="1")
    assert user.id == 1


def test_get_user_by_username(
    fake_user_repository: UserRepositoryProtocol,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("app.services.user_service.User", new=fake_user_repository)
    user = user_service.get_user(username_or_id="test_username")
    assert user.username == "test_username"


@pytest.mark.parametrize("identifier", ["1", "test_username"])
def test_get_not_existing_user(
    identifier: str,
    fake_empty_user_repository: UserRepositoryProtocol,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("app.services.user_service.User", new=fake_empty_user_repository)

    with pytest.raises(exceptions.UserDoesNotExists):
        user_service.get_user(username_or_id=identifier)
