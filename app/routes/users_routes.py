from flask import abort, jsonify, redirect, render_template, request, url_for

from app import app
from app import exceptions
from app.forms import EditProfileForm
from app.services import user_service, post_service


@app.route("/users/<string:username_or_id>", methods=["GET", "POST"])
def user_page(username_or_id: str):
    """Функция для обработки страницы пользователя"""
    try:
        user = user_service.get_user(username_or_id)
    except exceptions.UserDoesNotExists:
        abort(404)

    form = EditProfileForm()
    if form.validate_on_submit():
        user.update_from_form(form)
        username_or_id = form.username.data
        return redirect(url_for("user_page", username_or_id=username_or_id))

    form.fill_from_user_object(user)

    page = request.args.get("page", 1, type=int)
    posts = post_service.get_user_paginated_posts(user, page, request.args)
    return render_template(
        "user.html",
        user=user,
        form=form,
        current_page=page,
        posts=posts,
    )


@app.route("/user/<string:username>/posts", methods=["POST"])
def get_posts_by_user(username: str):
    """Функция для получения отсортированных записей для указанного автора"""
    try:
        user = user_service.get_user_by_username(username)
    except exceptions.UserDoesNotExists:
        abort(404)
    else:
        page = request.args.get("page", 1, type=int)
        posts = post_service.get_user_paginated_posts(user, page, request.args)
        html_data = render_template(
            "posts.html",
            posts=posts,
            current_page=page,
            type="user_posts",
            username=username,
        )
        return jsonify({"ok": True, "html_data": html_data})


@app.route("/user/<string:username>/subscriptions", methods=["POST"])
def get_subscriptions_by_user(username: str):
    """Функция для получения подписок пользователя"""
    try:
        user = user_service.get_user_by_username(username)
    except exceptions.UserDoesNotExists:
        abort(404)
    else:
        page = request.args.get("page", 1, type=int)
        groups = user_service.get_user_subscribed_groups(user, page)
        html_data = render_template(
            "subscriptions.html",
            groups=groups,
            current_page=page,
            username=user.username,
        )
        return jsonify({"ok": True, "html_data": html_data})
