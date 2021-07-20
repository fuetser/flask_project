from flask import render_template, request
from flask_login import current_user, login_required

from app import app
from app.services import post_service


@app.route("/my_feed")
@login_required
def my_feed_page():
    """Функция для обработки страницы персональной ленты новостей"""
    page = request.args.get("page", 1, type=int)
    posts = post_service.get_feed_posts(current_user, page)
    return render_template(
        "my_feed.html", posts=posts, active_link="my_feed", current_page=page
    )
