import http

import jwt
import pytest
import pytest_mock
import werkzeug.exceptions

from app.services import token_service

USERNAME = "foo"


@pytest.fixture
def valid_token() -> str:
    payload = {"username": USERNAME}
    return token_service.create_token(payload)


def test_validate_empty_token():
    with pytest.raises(werkzeug.exceptions.HTTPException) as err:
        token_service.validate_token(token="")

    assert err.value.code == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "exception",
    [
        jwt.ExpiredSignatureError(),
        jwt.InvalidSignatureError(),
        jwt.DecodeError(),
    ],
)
def test_validate_incorrect_token(
    exception: jwt.PyJWTError,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("app.services.token_service.jwt.decode", side_effect=exception)

    with pytest.raises(werkzeug.exceptions.HTTPException) as err:
        token_service.validate_token(token="test_token")

    assert err.value.code == http.HTTPStatus.UNAUTHORIZED


def test_validate_correct_token(valid_token: str):
    validated_token = token_service.validate_token(token=valid_token)

    assert "username" in validated_token
    assert validated_token["username"] == USERNAME


def test_is_valid_token_with_incorrect_token():
    is_valid_token = token_service.is_valid_token(token="test_token")
    assert not is_valid_token


def test_is_valid_token_with_correct_token(valid_token: str):
    is_valid_token = token_service.is_valid_token(token=valid_token)
    assert is_valid_token
