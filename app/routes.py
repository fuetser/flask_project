import os

from flask import render_template, flash, redirect, url_for, abort, request
from flask import jsonify, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required

from app import app, exceptions
from app.forms import *
from app.models import *
from app.utils import *


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
    if post is None:
        abort(404)

    try:
        comments = post.get_comments(request.args)
    except exceptions.IncorrectQueryParam:
        abort(404)
    else:
        return render_template("post.html", post=post, comments=comments)


@app.route("/users/<string:username_or_id>", methods=["GET", "POST"])
def user(username_or_id):
    if username_or_id.isdigit():
        user = User.query.get(int(username_or_id))
    else:
        user = User.get_by_username(username_or_id)
    if user is None:
        abort(404)

    form = EditProfileForm()
    if form.validate_on_submit():
        user.update_from_form(form)
        return redirect(url_for("user", username=form.username.data))
    elif request.method == "GET":
        form.fill_from_user_object(user)
    return render_template("user.html", user=user, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.create_from_form_and_get(form)
        except exceptions.ImageError:
            flash(str(e))
            return redirect(url_for("register"))
        else:
            login_user(user, remember=True)
            flash("Аккаунт успешно создан!", "success")
            return redirect(url_for("best"))

    return render_template("register.html", form=form, active_link="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("best"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.authorize_from_form_and_get(form)
        except exceptions.AuthorizationError:
            flash("Ошибка авторизации!", "danger")
            return redirect(url_for("login"))
        else:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("best"))

    return render_template("login.html", form=form, active_link="login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("best"))


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        try:
            group_id = request.args.get("group_id", -1)
            post = Post.from_form(current_user, group_id, form)
        except exceptions.GroupDoesNotExists:
            abort(404)
        except exceptions.ImageError as e:
            flash(str(e))
            return redirect(url_for("new_post", group_id=group_id))
        else:
            return redirect(url_for("group", group_id=group_id))

    return render_template("new_post.html", form=form)


@app.route("/group/<int:group_id>")
def group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        abort(404)
    return render_template("group.html", group=group)


@app.route("/subscribe/<int:group_id>", methods=["POST"])
def subscribe(group_id):
    group = Group.query.get(group_id)
    if group is None or not current_user.is_authenticated:
        abort(404)
    group.on_subscribe_click(current_user)
    return jsonify({"success": "OK"})


@app.route("/new_group", methods=["GET", "POST"])
@login_required
def new_group():
    form = NewGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        logo_bytes = convert_wtf_file_to_bytes(form.logo.data)
        if Group.is_unique_name(name):
            try:
                check_group_logo_validity(logo_bytes)
            except Exception as e:
                flash(str(e))
                return redirect(url_for("new_group"))
            else:
                group = Group(name=name, description=description)
                group.subscribers.append(current_user)
                db.session.add(group)
                db.session.commit()
                mimetype = get_mimetype_from_wtf_file(form.logo.data)
                logo = GroupLogo.from_bytes(logo_bytes, mimetype, group)
                flash("Группа успешно создана", "success")
                return redirect(url_for("best"))
        else:
            flash("Данное имя уже занято")
            return redirect(url_for("new_group"))

    return render_template("new_group.html", form=form)


@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    post = Post.get_by_id(post_id)
    if post is None or not current_user.is_authenticated:
        abort(404)
    post.on_like_click(current_user)
    return jsonify({"success": "OK"})


@app.route("/comment/<int:post_id>", methods=["POST"])
def create_comment(post_id):
    post = Post.get_by_id(post_id)
    if not post or not current_user.is_authenticated:
        abort(404)
    text = request.values.get("text")
    Comment.create(post_id=post_id, author_id=current_user.id, body=text)
    return jsonify({"success": "OK"})


@app.route("/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.get_by_id(comment_id)
    if not comment:
        abort(404)
    if current_user.is_authenticated and comment.author_id == current_user.id:
        comment.delete()
    return jsonify({"comments": localize_comments(
        len(Post.get_by_id(comment.post_id).comments))})


@app.route("/like_comment/<int:comment_id>", methods=["POST"])
def like_comment(comment_id):
    comment = Comment.get_by_id(comment_id)
    if comment is None or not current_user.is_authenticated:
        abort(404)
    comment.on_like_click(current_user)
    return jsonify({"success": "OK"})


@app.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)
    if current_user.is_authenticated and post.author_id == current_user.id:
        post.delete()
    return jsonify({"success": "OK"})


@app.route("/token")
@login_required
def view_tokens():
    return render_template(
        "tokens.html", token=create_token({"sub": current_user.id}))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/favicon/'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')
