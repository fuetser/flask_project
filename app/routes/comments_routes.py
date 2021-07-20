from flask import abort, jsonify, request, render_template
from flask_login import current_user

from app import app
from app import exceptions
from app.services import comment_service
from app.services import post_service
from app.utils import localize_comments


@app.route("/comment/<int:post_id>", methods=["POST"])
def create_comment(post_id: int):
    """Функция для обработки запроса на создание комментария"""
    try:
        assert current_user.is_authenticated
        post = post_service.get_post(post_id)
    except (AssertionError, exceptions.PostDoesNotExists):
        abort(404)
    else:
        text = request.values.get("text")
        comment_service.create_comment(post, current_user, text)
        html_data = render_template("comments.html", comments=post.comments)
        return jsonify({
            "html_data": html_data,
            "title": localize_comments(len(post.comments)),
        })


@app.route("/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id: int):
    """Обработка запроса на удаление комментария"""
    try:
        comment = comment_service.get_comment(comment_id)
        post = post_service.get_post(comment.post_id)
    except exceptions.CommentDoesNotExists:
        abort(404)
    else:
        response_data = comment_service.on_comment_delete(
            comment, post, current_user
        )
        return jsonify(response_data)


@app.route("/comment/<int:comment_id>/like", methods=["POST"])
def like_comment(comment_id: int):
    """Обработка запроса лайка комментария"""
    try:
        assert current_user.is_authenticated
        comment = comment_service.get_comment(comment_id)
    except (AssertionError, exceptions.CommentDoesNotExists):
        abort(404)
    else:
        response_data = comment_service.on_like_click(comment, current_user)
        return jsonify(response_data)
