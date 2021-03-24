import pytest
import requests


POSTS_URL = "http://localhost:5000/api/posts"
USERS_URL = "http://localhost:5000/api/users"
GROUPS_URL = "http://localhost:5000/api/groups"


def test_geting_all_posts():
    resp = requests.get(POSTS_URL)
    assert resp.json().get("status") == 200, "Wrong status code"


def test_geting_post_by_id():
    resp = requests.get(f"{POSTS_URL}/2")
    assert resp.json().get("status") == 200, "Wrong status code"


def test_wrong_post_id():
    resp = requests.get(f"{POSTS_URL}/0")
    assert resp.json().get("status") == 404, "Wrong status code"


def test_changing_post():
    resp = requests.put(f"{POSTS_URL}/3", json={"title": "New title"})
    assert resp.json().get("status") == 201, "Wrong status code"


def test_invalid_post_changing():
    resp = requests.put(f"{POSTS_URL}/2")
    assert resp.json().get("status") == 400, "Wrong status code"


def test_deleting_post():
    resp = requests.delete(f"{POSTS_URL}/3")
    assert resp.json().get("status") == 204, "Wrong status code"


def test_creating_post():
    resp = requests.post(POSTS_URL, json={
        "title": "Test post title",
        "body": "body for post",
        "author_id": 1,
        "group_id": 1
    })
    assert resp.json().get("status") == 201, "Wrong status code"


def test_invalid_post_creation():
    resp = requests.post(POSTS_URL)
    assert resp.json().get("status") == 400, "Wrong status code"


def test_geting_all_users():
    resp = requests.get(USERS_URL)
    assert resp.json().get("status") == 200, "Wrong status code"


def test_geting_user_by_username():
    resp = requests.get(f"{USERS_URL}/Raveness")
    assert resp.json().get("status") == 200, "Wrong status code"


def test_creating_user():
    resp = requests.post(USERS_URL, json={
        "username": "NewUser",
        "email": "newuser@mail.com",
        "password": "password"
    })
    assert resp.json().get("status") == 201, "Wrong status code"


def test_invalid_user_creation():
    resp = requests.post(USERS_URL)
    assert resp.json().get("status") == 400, "Wrong status code"


def test_deleting_user():
    resp = requests.delete(f"{USERS_URL}/NewUser")
    assert resp.json().get("status") == 204, "Wrong status code"


def test_changing_user():
    resp = requests.put(
        f"{USERS_URL}/NewCoolUser", json={"password": "password"})
    assert resp.json().get("status") == 201, "Wrong status code"


def test_change_name_to_taken():
    resp = requests.put(f"{USERS_URL}/NewCoolUser", json={"username": "Admin"})
    assert resp.json().get("status") == 400, "Wrong status code"


def test_extra_params_to_user_change():
    resp = requests.put(f"{USERS_URL}/NewCoolUser", json={"id": 1})
    assert resp.json().get("status") == 400, "Wrong status code"


def test_geting_all_groups():
    resp = requests.get(GROUPS_URL)
    assert resp.json().get("status") == 200, "Wrong status code"


def test_geting_group_by_id():
    resp = requests.get(f"{GROUPS_URL}/1")
    assert resp.json().get("status") == 200, "Wrong status code"


def test_creating_group():
    resp = requests.post(GROUPS_URL, json={
        "name": "Cool group",
        "description": "Description for new group"
    })
    assert resp.json().get("status") == 201, "Wrong status code"


def test_invalid_group_creation():
    resp = requests.post(GROUPS_URL)
    assert resp.json().get("status") == 400, "Wrong status code"


def test_deleting_group():
    resp = requests.delete(f"{GROUPS_URL}/3")
    assert resp.json().get("status") == 204, "Wrong status code"


def test_changing_group():
    resp = requests.put(f"{GROUPS_URL}/2", json={"description": "empty ://"})
    assert resp.json().get("status") == 201, "Wrong status code"


def test_invalid_group_changes():
    resp = requests.put(f"{GROUPS_URL}/1")
    assert resp.json().get("status") == 400, "Wrong status code"


if __name__ == '__main__':
    pytest.main([__file__])
