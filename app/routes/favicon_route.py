import os.path

from flask import send_from_directory

from app import app


@app.route("/favicon.ico")
def favicon():
    """Функция для обработки фавикона сайта"""
    return send_from_directory(
        os.path.join(app.root_path, "static/favicon/"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
