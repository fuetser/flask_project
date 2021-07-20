from flask import render_template
from flask_login import current_user, login_required

from app import app


@app.route("/token")
@login_required
def view_tokens():
    """Функция для обработки страницы API токенов"""
    token = current_user.token
    return render_template("tokens.html", token=token)
