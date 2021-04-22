import os

from flask import render_template, flash, redirect, url_for, abort, request
from flask import jsonify, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from markdown import markdown

from app import app, exceptions
from app.forms import *
from app.models import *
from app.utils import localize_comments
from app.services.search_service import search_by_query


@app.route("/")
@app.route("/best")
def best():
    page = request.args.get("page", 1, type=int)
    days = request.args.get("days", 1, type=int)
    if days not in (1, 7, 30, 365):
        abort(404)
    posts = Post.get_best(page, days)
    return render_template(
        "feed.html", posts=posts, active_link="best", current_page=page)


@app.route("/hot")
def hot():
    page = request.args.get("page", 1, type=int)
    posts = Post.get_hot(page)
    return render_template(
        "feed.html", posts=posts, active_link="hot", current_page=page)


@app.route("/search")
def sort():
    return render_template("search.html", active_link="sort")


@app.route("/my_feed")
@login_required
def my_feed():
    page = request.args.get("page", 1, type=int)
    posts = current_user.get_posts_from_subscribed_groups(page)
    return render_template(
        "my_feed.html", posts=posts, active_link="my_feed", current_page=page)


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
    try:
        user = User.query.get(int(username_or_id))
    except ValueError:
        user = None
    user = user or User.get_by_username(username_or_id)
    if user is None:
        abort(404)

    page = request.args.get("page", 1, type=int)
    form = EditProfileForm()
    if form.validate_on_submit():
        user.update_from_form(form)
        return redirect(url_for("user", username_or_id=form.username.data))
    elif request.method == "GET":
        form.fill_from_user_object(user)
    return render_template(
        "user.html", user=user, form=form, current_page=page)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("best"))

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
    page = request.args.get("page", 1, type=int)
    if group is None:
        abort(404)
    posts = group.get_paginated_posts(page)
    return render_template(
        "group.html", group=group, posts=posts, current_page=page)


@app.route("/new_group", methods=["GET", "POST"])
@login_required
def new_group():
    form = NewGroupForm()
    if form.validate_on_submit():
        group = Group.create_from_form_and_get(form, current_user)
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
        form.group = group
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
    try:
        results, search_by, request_text, current_page = search_by_query(
            request.args, request.values
        )
    except exceptions.InvalidSearchQuery:
        return jsonify({"ok": False})
    else:
        return jsonify({
            "ok": True,
            "html_data": render_template(
                "search_results.html",
                results=results,
                search_by=search_by,
                request_text=request_text,
                current_page=current_page
            )
        })


@app.route("/posts/<int:days>", methods=["POST"])
def get_posts_by_age(days):
    page = request.args.get("page", 1, type=int)
    posts_type = request.values.get("type", "best")
    if posts_type == "hot":
        posts = Post.get_hot(page)
    elif posts_type == "my_feed":
        posts = current_user.get_posts_from_subscribed_groups(page)
    else:
        posts = Post.get_best(page, days)
    return jsonify({
        "ok": True, "html_data": render_template(
            "posts.html", posts=posts, current_page=page, type=posts_type
        )
    })



@app.route("/group/<int:group_id>", methods=["POST"])
def get_posts_by_group(group_id):
    group = Group.get_by_id(group_id)
    page = request.args.get("page", 1, type=int)
    posts = group.get_paginated_posts(page)
    if not group:
        abort(404)
    return jsonify({
        "ok": True, "html_data": render_template(
            "posts.html", posts=posts, current_page=page,
            type="group", group_id=group.id)
    })


@app.route("/user_posts/<string:username>", methods=["POST"])
def get_posts_by_user(username):
    user = User.get_by_username(username)
    page = request.args.get("page", 1, type=int)
    if not user:
        abort(404)
    posts = user.get_paginated_posts(page)
    return jsonify({
        "ok": True, "html_data": render_template(
            "posts.html", posts=posts, current_page=page,
            type="user_posts", username=user.username)
    })


@app.route("/user_subscriptions/<string:username>", methods=["POST"])
def get_subscriptions_by_user(username):
    user = User.get_by_username(username)
    page = request.args.get("page", 1, type=int)
    if not user:
        abort(404)
    groups = user.get_paginated_subscriptions(page)
    return jsonify({
        "ok": True, "html_data": render_template(
            "subscriptions.html", groups=groups,
            current_page=page, username=user.username)
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
