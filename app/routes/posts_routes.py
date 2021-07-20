from flask import (
    abort,
    jsonify,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_login import current_user, login_required
from markdown import markdown

from app import app
from app import exceptions
from app.forms import NewPostForm
from app.services import post_service, user_service


@app.route("/")
@app.route("/best")
def best_posts_page():
    """Функция для обработки страницы Лучшее"""
    page = request.args.get("page", 1, type=int)
    days = request.args.get("days", 1, type=int)
    try:
        posts = post_service.get_best_posts(page, days)
    except exceptions.InvalidRequestArgs:
        abort(404)
    else:
        return render_template(
            "feed.html",
            posts=posts,
            active_link="best",
            current_page=page,
        )


@app.route("/hot")
def hot_posts_page():
    """Функция для обработки страницы Горячее"""
    page = request.args.get("page", 1, type=int)
    posts = post_service.get_hot_posts(page)
    return render_template(
        "feed.html",
        posts=posts,
        active_link="hot",
        current_page=page,
    )


@app.route("/posts/<int:post_id>")
def post_page(post_id: int):
    """Функция для обработки страницы записи"""
    try:
        post = post_service.get_post(post_id)
        comments = post_service.get_post_comments(post, request.args)
    except (
        exceptions.PostDoesNotExists,
        exceptions.IncorrectQueryParam,
    ):
        abort(404)
    else:
        if post.uses_markdown:
            post.body = markdown(post.body)
        else:
            post.body = post.body.replace("\n", "</br>")
        return render_template("post.html", post=post, comments=comments)


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post_form_page():
    """Функция для обработки страницы создания записи"""
    form = NewPostForm()
    if form.validate_on_submit():
        try:
            group_id = request.args.get("group_id", -1)
            post_service.create_post(current_user, group_id, form)
        except exceptions.GroupDoesNotExists:
            abort(404)
        else:
            return redirect(url_for("group_page", group_id=group_id))

    return render_template("new_post.html", form=form)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post_form_page(post_id: int):
    """Функция для обработки страницы редактирования записи"""
    try:
        post = post_service.get_post(post_id)
        assert current_user == post.author
    except (exceptions.PostDoesNotExists, AssertionError):
        abort(404)

    form = NewPostForm()
    if form.validate_on_submit():
        post_service.update_post_from_form(post, form)
        return redirect(url_for("post_page", post_id=post_id))

    if request.method == "GET":
        form.fill_from_post_object(post)

    return render_template("new_post.html", form=form)


@app.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id: int):
    """Функция для обработки запроса на удаление записи"""
    try:
        post = post_service.get_post(post_id)
    except exceptions.PostDoesNotExists:
        abort(404)
    else:
        if current_user == post.author:
            post.delete()
        return jsonify({"success": "OK"})


@app.route("/posts/<int:post_id>", methods=["POST"])
def get_sorted_comments(post_id: int):
    """Функция для получения отсортированных комментариев"""
    try:
        post = post_service.get_post(post_id)
        comments = post_service.get_post_comments(post, request.args)
    except (
        exceptions.PostDoesNotExists,
        exceptions.IncorrectQueryParam,
    ):
        abort(404)
    else:
        html_data = render_template("comments.html", comments=comments)
        return jsonify({"html_data": html_data})


@app.route("/post/<int:post_id>/like", methods=["POST"])
def like_post(post_id: int):
    """Функция для обработки запроса на лайк записи"""
    try:
        assert current_user.is_authenticated
        post = post_service.get_post(post_id)
    except (AssertionError, exceptions.PostDoesNotExists):
        abort(404)
    else:
        post.on_like_click(current_user)
        return jsonify({"success": "OK"})


@app.route("/get_posts/<int:days>", methods=["POST"])
def get_posts_by_age(days: int):
    """Функция для получения отсортированных записей"""
    page = request.args.get("page", 1, type=int)
    posts_type = request.values.get("type", "best")

    if posts_type == "hot":
        posts = post_service.get_hot_posts(page)
    elif posts_type == "my_feed":
        posts = user_service.get_user_subscribed_groups(current_user, page)
    else:
        posts = post_service.get_best_posts(page, days)

    html_data = render_template(
        "posts.html",
        posts=posts,
        current_page=page,
        type=posts_type,
    )

    return jsonify({"ok": True, "html_data": html_data})
