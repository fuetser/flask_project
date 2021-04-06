from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from .models import User


class RegisterForm(FlaskForm):
    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(), Email()])
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Зарегистрироватся")

    def validate_username(self, username):
        if not User.is_free_username(username.data):
            raise ValidationError(f"Имя {username.data} уже занято")

    def validate_email(self, email):
        if not User.is_free_email(email.data):
            raise ValidationError(f"Адрес {email.data} уже занят")


class LoginForm(FlaskForm):
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить данные")
    submit = SubmitField("Войти")


class NewPostForm(FlaskForm):
    title = StringField(
        "Заголовок", validators=[DataRequired(), Length(min=2, max=64)])
    content = StringField(
        "Содержание записи", validators=[DataRequired()], widget=TextArea())
    use_markdown = BooleanField("Использовать Markdown")
    image = FileField()
    submit = SubmitField("Опубликовать")


class NewGroupForm(FlaskForm):
    name = StringField(
        "Имя группы", validators=[DataRequired(), Length(max=32)])
    description = StringField("Описание группы", validators=[
        DataRequired(), Length(max=128)], widget=TextArea())
    logo = FileField()
    submit = SubmitField("Создать")


class EditProfileForm(FlaskForm):
    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(), Email()])
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)])
    old_password = PasswordField("Старый пароль")
    password = PasswordField("Новый пароль")
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[EqualTo("password")])
    submit = SubmitField("Сохранить")

    def validate_old_password(self, old_password):
        if current_user.is_authenticated and self.password.data:
            if not current_user.check_password(old_password.data):
                raise ValidationError("Неверный пароль")

    def validate_username(self, username):
        if not User.is_free_username(username.data):
            if current_user.is_authenticated and username.data != current_user.username:
                raise ValidationError(f"Имя {username.data} уже занято")

    def validate_email(self, email):
        if not User.is_free_email(email.data):
            if current_user.is_authenticated and email.data != current_user.email:
                raise ValidationError(f"Адрес {email.data} уже занят")

    def fill_from_user_object(self, user: User):
        self.username.data = user.username
        self.email.data = user.email
