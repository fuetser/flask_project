import datetime as dt

from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, exceptions
from app.utils import *


class BaseModel:
    @classmethod
    def get_by_id(ModelClass, id: int):
        return ModelClass.query.get(id)

    @classmethod
    def get_all(ModelClass, offset: int, limit: int):
        return ModelClass.query.offset(offset).limit(limit).all()

    @classmethod
    def create(ModelClass, **kwargs):
        model_instance = ModelClass(**kwargs)
        model_instance.update()

    @classmethod
    def create_and_get(ModelClass, **kwargs):
        model_instance = ModelClass(**kwargs)
        model_instance.update()
        return model_instance

    def update(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(UserMixin, db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(64), unique=True)
    registered = db.Column(db.DateTime, default=dt.datetime.utcnow)

    avatar = db.relationship("UserAvatar", uselist=False, backref="user")
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

    @property
    def elapsed(self):
        return get_elapsed(self.registered)

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter(User.username == username).first()

    @staticmethod
    def is_free_email(email: str) -> bool:
        return not db.session.query(
            db.exists().where(User.email == email)).scalar()

    @staticmethod
    def is_free_username(username: str) -> bool:
        return not db.session.query(
            db.exists().where(User.username == username)).scalar()

    @staticmethod
    def create(**kwargs):
        user = User(**kwargs)
        user.set_password(user.password_hash)
        user.update()

    @staticmethod
    def create_and_get(**kwargs):
        user = User(**kwargs)
        user.set_password(user.password_hash)
        user.update()
        return user

    @staticmethod
    def create_from_form_and_get(form):
        user = User.create_and_get(
            username=form.username.data,
            email=form.email.data,
            password_hash=form.password.data,
        )

        image_bytes = convert_wtf_file_to_bytes(form.avatar.data)
        UserAvatar.raise_for_image_validity(image_bytes)

        mimetype = get_mimetype_from_wtf_file(form.avatar.data)
        UserAvatar.from_bytes(image_bytes, mimetype, user)

        return user

    def update_from_data(self, password_changed=False, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__ and value:
                setattr(self, key, value)
        self.update(password_changed=password_changed)

    def update(self, password_changed=False):
        if password_changed:
            self.set_password(self.password_hash)
        super().update()

    def delete(self):
        self.on_delete()
        super().delete()

    def on_delete(self):
        for group in self.groups:
            group.subscribers.remove(self)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserAvatar(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    b64string = db.Column(db.String)
    mimetype = db.Column(db.String(16))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @staticmethod
    def from_bytes(image_bytes: bytes, mimetype: str, user: User):
        b64string = convert_bytes_to_b64string(image_bytes)
        UserAvatar.create(b64string=b64string, mimetype=mimetype, user=user)

    @staticmethod
    def raise_for_image_validity(image_bytes):
        try:
            raise_for_user_avatar_validity(image_bytes)
        except Exception as e:
            raise exceptions.ImageError(str(e)) from e


posts_likes = db.Table(
    "posts_likes",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Post(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    picture = db.Column(db.LargeBinary, nullable=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    image = db.relationship("PostImage", uselist=False, backref="post")
    comments = db.relationship("Comment", backref="post")
    likes = db.relationship(
        "User", secondary=posts_likes, backref="post_likes")

    @property
    def elapsed(self):
        return get_elapsed(self.timestamp)

    @staticmethod
    def get_best():
        sub = db.session.query(
            posts_likes.c.post_id,
            func.count(posts_likes.c.user_id).label("count")
        ).group_by(posts_likes.c.post_id) \
         .subquery()

        posts = db.session.query(Post, sub.c.count) \
            .outerjoin(sub, Post.id == sub.c.post_id) \
            .order_by(db.desc("count")) \
            .all()

        # remove count attribute
        posts = map(lambda pair: pair[0], posts)
        return posts

    @staticmethod
    def get_hot():
        # TODO
        return Post.get_best()

    @staticmethod
    def from_form(author, group_id, form):
        group = Group.get_by_id(group_id)
        if group is None:
            raise exceptions.GroupDoesNotExists(
                f"Group {group_id} does not exists")

        image_bytes = convert_wtf_file_to_bytes(form.image.data)
        PostImage.raise_for_image_validity(image_bytes)

        post = Post.create_and_get(
            title=form.title.data,
            body=form.content.data,
            author=author,
            group=group,
        )
        mimetype = get_mimetype_from_wtf_file(form.image.data)
        PostImage.from_bytes(image_bytes, mimetype, post)

    def get_comments_by_likes(self, reverse: bool):
        return sorted(
            self.comments, key=lambda comm: len(comm.likes), reverse=reverse)

    def get_comments_by_date(self, reverse: bool):
        return sorted(
            self.comments, key=lambda comm: comm.timestamp, reverse=reverse)


class PostImage(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    b64string = db.Column(db.String)
    mimetype = db.Column(db.String(16))

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    @staticmethod
    def from_bytes(image_bytes: bytes, mimetype: str, post: Post):
        b64string = convert_bytes_to_b64string(image_bytes)
        PostImage.create(b64string=b64string, mimetype=mimetype, post=post)

    @staticmethod
    def raise_for_image_validity(image_bytes):
        try:
            raise_for_image_validity(image_bytes)
        except Exception as e:
            raise exceptions.ImageError(str(e)) from e


groups_subscribers = db.Table(
    "groups_subscribers",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Group(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    logo = db.relationship("GroupLogo", uselist=False, backref="group")
    posts = db.relationship("Post", backref="group")
    subscribers = db.relationship(
        "User", secondary=groups_subscribers, backref="groups")

    @staticmethod
    def is_unique_name(name: str) -> bool:
        return not db.session.query(
            db.exists().where(Group.name == name)).scalar()


class GroupLogo(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    b64string = db.Column(db.String)
    mimetype = db.Column(db.String(16))

    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    @staticmethod
    def from_bytes(image_bytes: bytes, mimetype: str, group: Group):
        b64string = convert_bytes_to_b64string(image_bytes)
        GroupLogo.create(b64string=b64string, mimetype=mimetype, group=group)


comments_likes = db.Table(
    "comments_likes",
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Comment(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    body = db.Column(db.Text())
    is_reply = db.Column(db.Boolean, default=False)
    reply_to = db.Column(db.Integer, nullable=True)  # db.ForeignKey("comment.id")
    # replies = db.relationship("Comment", lazy="dinamic")
    likes = db.relationship(
        "User", secondary=comments_likes, backref="comment_likes")

    @property
    def elapsed(self):
        return get_elapsed(self.timestamp)
