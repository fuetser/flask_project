from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import app
from app import exceptions
from app.forms import LoginForm, RegisterForm
from app.services import user_service


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Функция для обработки страницы авторизации"""
    if current_user.is_authenticated:
        return redirect(url_for("best_posts_page"))

    form = LoginForm()
    if form.validate_on_submit():
        return handle_login_form(form)

    return render_template("login.html", form=form, active_link="login")


def handle_login_form(form):
    """Обработка формы авторизации"""
    try:
        user = user_service.authorize_from_form(form)
    except exceptions.AuthorizationError:
        flash("Ошибка авторизации!", "danger")
        return redirect(url_for("login_page"))
    else:
        remember = form.remember.data
        login_user(user, remember=remember)
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        else:
            return redirect(url_for("best_posts_page"))


@app.route("/logout")
def logout():
    """Функция для обработки выхода пользователя из аккаунта"""
    logout_user()
    return redirect(url_for("best_posts_page"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Функция для обработки страницы регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for("best_posts_page"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = user_service.create_user(form)
        login_user(user, remember=True)
        flash("Аккаунт успешно создан!", "success")
        return redirect(url_for("best_posts_page"))

    return render_template("register.html", form=form, active_link="register")
