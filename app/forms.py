from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
)

from .models import User, Group
from app import exceptions
from app.services.image_service import RawImage


class RegisterForm(FlaskForm):
    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(), Email()]
    )
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)]
    )
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    avatar = FileField("Выберите аватар", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироватся")

    def validate_username(self, username):
        if not User.is_free_username(username.data):
            raise ValidationError(f"Имя {username.data} уже занято")

    def validate_email(self, email):
        if not User.is_free_email(email.data):
            raise ValidationError(f"Адрес {email.data} уже занят")

    def validate_avatar(self, avatar):
        raw_image = RawImage.from_wtf_file(avatar.data)
        try:
            raw_image.raise_for_image_validity()
        except exceptions.ImageError:
            raise ValidationError("Некорректное изображение")
        else:
            self.avatar.data = raw_image


class LoginForm(FlaskForm):
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)]
    )
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить данные")
    submit = SubmitField("Войти")


class NewPostForm(FlaskForm):
    title = StringField(
        "Заголовок", validators=[DataRequired(), Length(min=2, max=64)]
    )
    content = StringField(
        "Содержание записи", validators=[DataRequired()], widget=TextArea()
    )
    use_markdown = BooleanField("Использовать Markdown")
    image = FileField("Выберите картинку (необязательно)")
    submit = SubmitField("Опубликовать")

    def validate_image(self, image):
        if image.data is not None:
            raw_image = RawImage.from_wtf_file(image.data)
            try:
                raw_image.raise_for_image_validity()
            except exceptions.ImageError:
                raise ValidationError("Некорректное изображение")
            else:
                self.image.data = raw_image

    def fill_from_post_object(self, post):
        self.title.data = post.title
        self.content.data = post.body
        self.use_markdown.data = post.uses_markdown
        self.submit.label.text = "Сохранить"


class NewGroupForm(FlaskForm):
    name = StringField(
        "Имя группы", validators=[DataRequired(), Length(max=32)]
    )
    description = StringField(
        "Описание группы",
        validators=[DataRequired(), Length(max=128)],
        widget=TextArea(),
    )
    logo = FileField("Выберите логотип", validators=[DataRequired()])
    submit = SubmitField("Создать")

    def validate_name(self, name):
        if not Group.is_unique_name(name.data):
            raise ValidationError(f"Название {name.data} уже занято")

    def validate_logo(self, logo):
        raw_image = RawImage.from_wtf_file(logo.data)
        try:
            raw_image.raise_for_image_validity()
        except exceptions.ImageError:
            raise ValidationError("Некорректное изображение")
        else:
            self.logo.data = raw_image


class EditGroupForm(FlaskForm):
    name = StringField(
        "Имя группы", validators=[DataRequired(), Length(max=32)]
    )
    description = StringField(
        "Описание группы",
        validators=[DataRequired(), Length(max=128)],
        widget=TextArea(),
    )
    logo = FileField("Выберите логотип")
    # поле для хранения изначального названия группы
    __group_name = StringField()
    submit = SubmitField("Сохранить")

    def fill_from_group_object(self, group):
        self.name.data = group.name
        self.description.data = group.description
        self.__group_name.data = group.name

    def validate_name(self, name):
        if (
            not Group.is_unique_name(name.data)
            and name.data != self.__group_name.data
        ):
            raise ValidationError(f"Название {name.data} уже занято")

    def validate_logo(self, logo):
        if logo.data:
            raw_image = RawImage.from_wtf_file(logo.data)
            try:
                raw_image.raise_for_image_validity()
            except exceptions.ImageError:
                raise ValidationError("Некорректное изображение")
            else:
                self.logo.data = raw_image


class EditProfileForm(FlaskForm):
    email = StringField(
        "Адрес электронной почты", validators=[DataRequired(), Email()]
    )
    username = StringField(
        "Имя пользователя", validators=[DataRequired(), Length(min=3, max=25)]
    )
    old_password = PasswordField("Старый пароль")
    password = PasswordField("Новый пароль")
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[EqualTo("password")]
    )
    image = FileField("Выберите аватар")
    submit = SubmitField("Сохранить")

    def validate_old_password(self, old_password):
        if current_user.is_authenticated and self.password.data:
            if not current_user.check_password(old_password.data):
                raise ValidationError("Неверный пароль")

    def validate_username(self, username):
        if not User.is_free_username(username.data):
            if (
                current_user.is_authenticated
                and username.data != current_user.username
            ):
                raise ValidationError(f"Имя {username.data} уже занято")

    def validate_email(self, email):
        if not User.is_free_email(email.data):
            if (
                current_user.is_authenticated
                and email.data != current_user.email
            ):
                raise ValidationError(f"Адрес {email.data} уже занят")

    def validate_image(self, image):
        if image.data:
            raw_image = RawImage.from_wtf_file(image.data)
            try:
                raw_image.raise_for_image_validity()
            except exceptions.ImageError:
                raise ValidationError("Некорректное изображение")
            else:
                self.image.data = raw_image

    def fill_from_user_object(self, user: User):
        self.username.data = user.username
        self.email.data = user.email
