import pytest
import requests


POSTS_URL = "http://localhost:5000/api/posts"
USERS_URL = "http://localhost:5000/api/users"
GROUPS_URL = "http://localhost:5000/api/groups"
TOKEN_URL = "http://localhost:5000/api/tokens"

USERNAME = "originalUsername"
PASSWORD = "somePassword"
EMAIL = "original_email@mail.com"
USER_ID = 1
GROUP_ID = 1
POST_ID = 1
TOKEN = ""


def test_request_without_token():
    resp = requests.get(POSTS_URL)
    assert resp.json().get("status") == 401, "Access without token provided"


def test_creating_user():
    resp = requests.post(
        USERS_URL,
        json={"username": USERNAME, "password": PASSWORD, "email": EMAIL},
    )
    assert resp.json().get("status") == 201, "Unable to create user"


def test_invalid_user_creation():
    resp = requests.post(USERS_URL)
    assert resp.json().get("status") == 400, "User shouldn't have been created"


def test_geting_api_token():
    global TOKEN
    resp = requests.post(
        TOKEN_URL, json={"username": USERNAME, "password": PASSWORD}
    )
    token = resp.json().get("token")
    assert token is not None, "Unable to get token with given credentials"
    TOKEN = token


def test_geting_user_id():
    global USER_ID
    resp = requests.get(USERS_URL, params={"token": TOKEN})
    users = resp.json().get("users")
    assert users is not None, "Unable to get all users list"
    USER_ID = users[-1]["id"]


def test_creating_group():
    resp = requests.post(
        GROUPS_URL,
        json={
            "name": "Original name for group",
            "description": "Description for original group",
            "admin_id": USER_ID,
        },
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 201, "Unable to create group"


def test_geting_group_id():
    global GROUP_ID
    resp = requests.get(GROUPS_URL, params={"token": TOKEN})
    groups = resp.json().get("groups")
    assert groups is not None, "Unable to get all groups list"
    GROUP_ID = groups[-1]["id"]


def test_creating_post():
    resp = requests.post(
        POSTS_URL,
        json={
            "title": "Test post title",
            "body": "Body for post",
            "author_id": USER_ID,
            "group_id": GROUP_ID,
        },
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 201, "Unable to create post"


def test_geting_all_posts():
    global POST_ID
    resp = requests.get(POSTS_URL, params={"token": TOKEN})
    posts = resp.json().get("posts")
    assert posts is not None, "Unable to get all posts list"
    POST_ID = posts[-1]["id"]


def test_invalid_post_creation():
    resp = requests.post(POSTS_URL, params={"token": TOKEN})
    assert resp.json().get("status") == 400, "Post with no data created"


def test_geting_post_by_id():
    resp = requests.get(f"{POSTS_URL}/{POST_ID}", params={"token": TOKEN})
    assert resp.json().get("status") == 200, "Unable to get post by id"


def test_wrong_post_id():
    resp = requests.get(f"{POSTS_URL}/0", params={"token": TOKEN})
    assert resp.json().get("status") == 404, "Got post with not existing id"


def test_changing_post():
    resp = requests.put(
        f"{POSTS_URL}/{POST_ID}",
        json={"title": "New title"},
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 201, "Unable to change post"


def test_invalid_post_changing():
    resp = requests.put(f"{POSTS_URL}/{POST_ID}", params={"token": TOKEN})
    assert resp.json().get("status") == 400, "Post changed with no data"


def test_deleting_post():
    resp = requests.delete(f"{POSTS_URL}/{POST_ID}", params={"token": TOKEN})
    assert resp.json().get("status") == 204, "Unable to delete post"


def test_geting_user_by_username():
    resp = requests.get(f"{USERS_URL}/{USERNAME}", params={"token": TOKEN})
    assert resp.json().get("status") == 200, "Unable to get user by username"


def test_changing_user():
    resp = requests.put(
        f"{USERS_URL}/{USERNAME}",
        json={"password": "new_password"},
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 201, "Unable to change user"


def test_change_name_to_taken():
    resp = requests.put(
        f"{USERS_URL}/{USERNAME}",
        json={"username": USERNAME},
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 400, "Username changet to taken one"


def test_extra_params_to_user_change():
    resp = requests.put(
        f"{USERS_URL}/{USERNAME}",
        json={"key": "value"},
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 400, "Extra params in request allowed"


def test_geting_group_by_id():
    resp = requests.get(f"{GROUPS_URL}/{GROUP_ID}", params={"token": TOKEN})
    assert resp.json().get("status") == 200, "Unable to get group"


def test_invalid_group_creation():
    resp = requests.post(GROUPS_URL, params={"token": TOKEN})
    assert resp.json().get("status") == 400, "Group created with no data"


def test_invalid_group_changes():
    resp = requests.put(
        f"{GROUPS_URL}/{GROUP_ID}",
        json={"key": "value"},
        params={"token": TOKEN},
    )
    assert resp.json().get("status") == 400, "Group changed with invalid data"


def test_deleting_group():
    resp = requests.delete(f"{GROUPS_URL}/{GROUP_ID}", params={"token": TOKEN})
    assert resp.json().get("status") == 204, "Unable to delete group"


def test_deleting_user():
    resp = requests.delete(f"{USERS_URL}/{USERNAME}", params={"token": TOKEN})
    assert resp.json().get("status") == 204, "Unable to delete user"


if __name__ == "__main__":
    pytest.main([__file__])
