from app import exceptions
from app.models import Comment
from app.utils import localize_comments


def get_comment(comment_id: int) -> Comment:
    """Получения комментария по его ID"""
    comment = Comment.get_by_id(comment_id)
    if comment is None:
        raise exceptions.CommentDoesNotExists()
    return comment


def create_comment(post, author, text):
    """Создание комментария"""
    Comment.create(post=post, author=author, body=text)


def on_comment_delete(comment, post, user):
    """Обработка попытки удаления комментария"""
    if user == comment.author:
        comment.delete()

    response_data = {"title": localize_comments(len(post.comments))}
    return response_data


def on_like_click(comment, user):
    """Метод для обработки лайка комментария"""
    if user in comment.likes:
        comment.likes.remove(user)
    else:
        comment.likes.append(user)
    comment.update()

    response_data = {"success": "OK"}
    return response_data
