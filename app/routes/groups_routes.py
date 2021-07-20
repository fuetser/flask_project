from flask import abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import app
from app import exceptions
from app.forms import NewGroupForm, EditGroupForm
from app.services import group_service
from app.utils import localize_subscribers


@app.route("/group/<int:group_id>")
def group_page(group_id: int):
    """Функция для обработки страницы группы"""
    try:
        group = group_service.get_group(group_id)
    except exceptions.GroupDoesNotExists:
        abort(404)
    else:
        page = request.args.get("page", 1, type=int)
        posts = group.get_paginated_posts(page, request.args)
        subscribers = localize_subscribers(len(group.subscribers))
        return render_template(
            "group.html",
            group=group,
            posts=posts,
            subscribers=subscribers,
            current_page=page,
        )


@app.route("/new_group", methods=["GET", "POST"])
@login_required
def new_group_form_page():
    """Функция для обработки страницы создания группы"""
    form = NewGroupForm()
    if form.validate_on_submit():
        group = group_service.create_group(form, current_user)
        return redirect(url_for("group_page", group_id=group.id))

    return render_template("new_group.html", form=form)


@app.route("/group/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def edit_group_form_page(group_id: int):
    """Функция для обработки страницы редактирования группы"""
    try:
        group = group_service.get_group(group_id)
        assert current_user == group.admin
    except (exceptions.GroupDoesNotExists, AssertionError):
        abort(404)
    else:
        form = EditGroupForm()
        if form.validate_on_submit():
            group.update_from_form(form)
            return redirect(url_for("group_page", group_id=group.id))

        if request.method == "GET":
            form.fill_from_group_object(group)
            form.group = group

        return render_template("new_group.html", form=form, group_id=group.id)


@app.route("/group/<int:group_id>", methods=["DELETE"])
def delete_group(group_id: int):
    """Функция для обработки запроса на удаление группы"""
    try:
        group = group_service.get_group(group_id)
    except exceptions.GroupDoesNotExists:
        abort(404)
    else:
        if current_user == group.admin:
            group.delete()
        return jsonify({"success": "OK"})


@app.route("/group/<int:group_id>", methods=["POST"])
def get_posts_by_group(group_id: int):
    """Функция для получения отсортированных записей для указанной группы"""
    try:
        group = group_service.get_group(group_id)
    except exceptions.GroupDoesNotExists:
        abort(404)
    else:
        page = request.args.get("page", 1, type=int)
        posts = group.get_paginated_posts(page, request.args)
        html_data = render_template(
            "posts.html",
            posts=posts,
            current_page=page,
            type="group",
            group_id=group.id,
        )
        return jsonify({"ok": True, "html_data": html_data})


@app.route("/group/<int:group_id>/subscribe", methods=["POST"])
def subscribe_to_group(group_id: int):
    """Функция для обработки запроса на подписку"""
    try:
        assert current_user.is_authenticated
        group = group_service.get_group(group_id)
    except (AssertionError, exceptions.GroupDoesNotExists):
        abort(404)
    else:
        response_data = group_service.on_subscribe_click(group, current_user)
        return jsonify(response_data)
