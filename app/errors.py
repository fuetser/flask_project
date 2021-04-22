from flask import render_template

from app import app


error_decriptions = {
    403: (
        "У Вас недостаточно прав для доступа к данной странице",
        "Проверьте свой профиль и повторите попытку позже",
    ),
    404: (
        "Похоже, запрашиваемая страница не существует",
        "Проверьте правильность запроса и повторите попытку позже",
    ),
    500: (
        "В данный момент сервер не может обработать Ваш запрос",
        "Повторите попытку позже",
    ),
}

error_titles = {
    403: "Доступ запрещён",
    404: "Страница не найдена",
    500: "Ошибка сервера",
}


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    error = error.code
    return (
        render_template(
            "error.html",
            error_code=error,
            title=error_titles[error],
            description=error_decriptions[error],
        ),
        error,
    )
