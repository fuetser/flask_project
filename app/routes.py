from flask import render_template, flash, redirect, url_for
from flask.json import jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.forms import *
from app.models import *


@app.route("/")
@app.route("/best")
def best():
    posts = Post.get_best()
    return render_template("feed.html", posts=posts, active_link="best")


@app.route("/hot")
def hot():
    posts = Post.get_hot()
    return render_template("feed.html", posts=posts, active_link="hot")


@app.route("/sort")
def sort():
    return render_template("base.html", active_link="sort")


@app.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get(post_id)
    if post is not None:
        return render_template("post.html", post=post)


@app.route("/users/<int:user_id>")
def user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        return render_template("user.html", user=user)


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
            login_user(user, remember=True)
            flash("Аккаунт успешно создан!", "success")
            return redirect(url_for("best"))

        else:
            flash("Аккаунт с такой почтой или именем уже существует!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html", form=form, active_link="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("best"))
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


@app.route("/group/<int:group_id>")
def group(group_id):
    group = Group.query.get(group_id)
    if group is not None:
        return render_template("group.html", group=group)


@app.route("/subscribe/<int:group_id>", methods=["POST"])
@login_required
def subscribe(group_id):
    group = Group.query.get(group_id)
    if group is not None:
        if current_user in group.subscribers:
            group.subscribers.remove(current_user)
        else:
            group.subscribers.append(current_user)
        db.session.commit()
        return jsonify({"success": "OK"})
    return jsonify({"error": "Group doesn't exists"})


@login_required
@app.route("/new_group", methods=["GET", "POST"])
def new_group():
    form = NewGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        if Group.is_unique_name(name):
            group = Group(name=name, description=description)
            group.subscribers.append(current_user)
            db.session.add(group)
            db.session.commit()
            flash("Группа успешно создана", "success")
            return redirect(url_for("best"))
        else:
            flash("Данное имя уже занято")
            return redirect(url_for("new_group"))

    return render_template("new_group.html", form=form)
