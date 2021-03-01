from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.forms import LoginForm, RegisterForm, NewPostForm
from app.models import *


LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Cras venenatis vehicula libero et elementum. Sed imperdiet velit "
    "tristique tempor sagittis. Donec sodales diam quam, in tempor dolor "
    "faucibus tempus. Nulla dui erat, ultricies non facilisis non, eleifend "
    "eu felis. Proin vel turpis ante. Suspendisse in odio nec nisi pulvinar "
    "aliquam.".split())

lorem_ipsum = (lambda n: " ".join(LOREM_IPSUM[:n]))

POST_EXAMPLE = {
    "id": 456,
    "author": {"nickname": "bad_user", "id": 5678},
    "title": "Dogs aren't so cute!",
    "elapsed": "1 hour ago",
    "body": lorem_ipsum(20),
    "likes": 1000,
    "comments": 12,
}

USER_EXAMPLE = {
    "id": 123,
    "nickname": "bad_user",
    "posts": [POST_EXAMPLE] * 5,
}


@app.route("/")
@app.route("/best")
def best():
    return render_template(
        "feed.html", posts=[POST_EXAMPLE] * 5, active_link="best")


@app.route("/hot")
def hot():
    return render_template(
        "feed.html", posts=[POST_EXAMPLE] * 10, active_link="hot")


@app.route("/sort")
def sort():
    return render_template("base.html", active_link="sort")


@app.route("/posts/<int:post_id>")
def post(post_id):
    return render_template("post.html", post=POST_EXAMPLE)


@app.route("/users/<int:user_id>")
def user(user_id):
    return render_template("user.html", user=USER_EXAMPLE)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        user = User.get_by_username(username)
        is_free_email = User.is_free_email(email)

        if user is None and is_free_email:
            user = User(email=email, username=username)
            password = form.password.data
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Аккаунт успешно создан!", "success")
            return redirect(url_for("best"))

        else:
            flash("Аккаунт с такой почтой или именем уже существует!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html", form=form, active_link="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get_by_username(username)
        if user is not None and user.check_password(password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("best"))
        else:
            flash("Ошибка авторизации!", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, active_link="login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("best"))


@login_required
@app.route("/new_post", methods=["GET", "POST"])
def create_new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        flash("Запись успешно создана", "success")
        return redirect(url_for("best"))
    return render_template("new_post.html", form=form)
