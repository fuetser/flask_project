from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(), Email()])
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Зарегистрироватся")


class LoginForm(FlaskForm):
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить данные")
    submit = SubmitField("Войти")
