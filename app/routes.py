import os

from flask import render_template, flash, redirect, url_for, abort, request
from flask import jsonify, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from markdown import markdown

from app import app, exceptions
from app.forms import *
from app.models import *
from app.utils import localize_comments
from app.services.token_service import create_token


@app.route("/")
@app.route("/best")
def best():
    posts = Post.get_best()
    return render_template("feed.html", posts=posts, active_link="best")


@app.route("/hot")
def hot():
    posts = Post.get_hot()
    return render_template("feed.html", posts=posts, active_link="hot")


@app.route("/search")
def sort():
    return render_template("search.html", active_link="sort")


@app.route("/my_feed")
@login_required
def my_feed():
    posts = current_user.get_posts_from_subscribed_groups()
    return render_template("my_feed.html", posts=posts, active_link="my_feed")


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
        if post.uses_markdown:
            post.body = markdown(post.body)
        else:
            post.body = post.body.replace("\n", "</br>")
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
        return redirect(url_for("user", username_or_id=form.username.data))
    elif request.method == "GET":
        form.fill_from_user_object(user)
    return render_template("user.html", user=user, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create_from_form_and_get(form)
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
        else:
            return redirect(url_for("group", group_id=group_id))

    return render_template("new_post.html", form=form)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    if not post or post.author != current_user:
        abort(404)
    form = NewPostForm()
    if form.validate_on_submit():
        post.update_from_form(form)
        return redirect(url_for("post", post_id=post_id))
    elif request.method == "GET":
        form.fill_from_post_object(post)
    return render_template("new_post.html", form=form)


@app.route("/group/<int:group_id>")
def group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        abort(404)
    return render_template("group.html", group=group)


@app.route("/new_group", methods=["GET", "POST"])
@login_required
def new_group():
    form = NewGroupForm()
    if form.validate_on_submit():
        try:
            group = Group.create_from_form_and_get(form, current_user)
        except exceptions.NotUniqueGroupName:
            flash("Данное имя уже занято")
            return redirect(url_for("new_group"))
        else:
            return redirect(url_for("group", group_id=group.id))

    return render_template("new_group.html", form=form)


@app.route("/group/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def edit_group(group_id):
    group = Group.get_by_id(group_id)
    if not group or group.admin_id != current_user.id:
        abort(404)
    form = EditGroupForm()
    if form.validate_on_submit():
        group.update_from_form(form)
        return redirect(url_for("group", group_id=group.id))
    elif request.method == "GET":
        form.fill_from_group_object(group)
    return render_template("new_group.html", form=form, group_id=group.id)


@app.route("/subscribe/<int:group_id>", methods=["POST"])
def subscribe(group_id):
    group = Group.query.get(group_id)
    if group is None or not current_user.is_authenticated:
        abort(404)
    group.on_subscribe_click(current_user)
    return jsonify({"success": "OK"})


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
    if post is None or not current_user.is_authenticated:
        abort(404)
    text = request.values.get("text")
    Comment.create(post=post, author=current_user, body=text)
    return jsonify({
        "html_data": render_template("comments.html", comments=post.comments),
        "title": localize_comments(len(post.comments))
    })


@app.route("/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.get_by_id(comment_id)
    if comment is None:
        abort(404)
    if current_user == comment.author:
        comment.delete()
    return jsonify({"title": localize_comments(
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
    if current_user == post.author:
        post.delete()
    return jsonify({"success": "OK"})


@app.route("/group/<int:group_id>", methods=["DELETE"])
def delete_group(group_id):
    group = Group.get_by_id(group_id)
    if not group:
        abort(404)
    if group.admin_id == current_user.id:
        group.delete()
    return jsonify({"success": "OK"})


@app.route("/search", methods=["POST"])
def get_search_results():
    page = request.args.get("page", 1, type=int)
    request_text = request.values.get("request_text", "").strip()
    search_groups = request.values.get("search_groups") == "true"
    search_users = request.values.get("search_users") == "true"
    search_posts = request.values.get("search_posts") == "true"
    if not request_text or not (search_groups or search_users or search_posts):
        return jsonify({"ok": False})
    elif search_groups:
        search_results = Group.get_similar(request_text, page=page)
    elif search_users:
        search_results = User.get_similar(request_text, page=page)
    else:
        search_results = Post.get_similar(request_text, page=page)
    return jsonify({
        "ok": True,
        "html_data": render_template(
            "search_results.html", results=search_results,
            search_groups=search_groups, search_users=search_users,
            text=request_text, current_user=current_user)
    })


@app.route("/token")
@login_required
def view_tokens():
    return render_template("tokens.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/favicon/'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')
