from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.widgets import TextArea
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


class NewPostForm(FlaskForm):
    title = StringField(
        "Заголовок", validators=[DataRequired(), Length(min=2, max=64)])
    content = StringField(
        "Содержание записи", validators=[DataRequired()], widget=TextArea())
    use_markdown = BooleanField("Использовать Markdown")
    files = FileField(validators=[FileRequired()])
    submit = SubmitField("Опубликовать")


class NewGroupForm(FlaskForm):
    name = StringField("Имя группы", validators=[DataRequired(), Length(max=32)])
    description = StringField("Описание группы",
        validators=[DataRequired(), Length(max=128)], widget=TextArea())
    submit = SubmitField("Создать")
