from app import exceptions
from app.models import Post, PostImage
from app.services import group_service
from config import Config


def get_post(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        raise exceptions.PostDoesNotExists()
    return post


def get_best_posts(page, days):
    """Получение лучших постов по запросу"""
    if days not in (1, 7, 30, 365):
        raise exceptions.InvalidRequestArgs()

    posts = Post.get_best(page, days)
    return posts


def get_hot_posts(page):
    """Получение горячих постов по запросу"""
    posts = Post.get_hot(page)
    return posts


def create_post(author, group_id, form):
    """Создание нового поста"""
    group = group_service.get_group(group_id)
    post = create_post_from_form(form, author, group)

    image = form.image.data
    if image is not None:
        create_post_image(image, post)


def create_post_from_form(form, author, group) -> Post:
    """Создание поста по данным из формы"""
    post = Post.create_and_get(
        title=form.title.data,
        body=form.content.data,
        author=author,
        group=group,
        uses_markdown=form.use_markdown.data,
    )
    return post


def create_post_image(image, post) -> None:
    """Создание картинки для поста"""
    PostImage.from_raw_image(image, post)


def update_post_from_form(post, form) -> None:
    """Обновление поста по данным из формы"""
    post.title = form.title.data
    post.body = form.content.data
    post.uses_markdown = form.use_markdown.data

    image = form.image.data
    if image:
        image.raise_for_image_validity()
        create_post_image(image, post)

    post.update()


def get_feed_posts(user, page):
    """Получение постов из подписок пользователя"""
    groups_ids = [group.id for group in user.groups]
    posts = Post.query.filter(Post.group_id.in_(groups_ids)).paginate(
        page=page, per_page=Config.POSTS_PER_PAGE
    )
    return posts


def get_post_comments(post, query_params):
    """Получение отсортированных комментариев данного поста"""
    sort_comments_by = query_params.get("sort", "popular")
    if sort_comments_by not in ("date", "popular"):
        raise exceptions.IncorrectQueryParam("Incorrect query param: 'sort'")

    if sort_comments_by == "date":
        keyfunc = lambda comment: comment.timestamp  # noqa: E731
    elif sort_comments_by == "popular":
        keyfunc = lambda comment: len(comment.likes)  # noqa: E731

    reverse = query_params.get("reverse") == "true"
    return sorted(post.comments, key=keyfunc, reverse=reverse)


def get_user_paginated_posts(user, page, request_args):
    """Получение записей пользователя по страницам"""
    reverse = request_args.get("reverse") == "true"
    if request_args.get("sort") == "popular":
        query = Post.get_best_posts_query(desc_order=reverse).filter(
            Post.author_id == user.id
        )
    else:
        base_query = Post.query.filter(Post.author_id == user.id)
        if reverse:
            query = base_query.order_by(Post.timestamp.desc())
        else:
            query = base_query.order_by(Post.timestamp.asc())

    return query.paginate(
        page=page, per_page=Config.POSTS_PER_PAGE, error_out=False
    )
