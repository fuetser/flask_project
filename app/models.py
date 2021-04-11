import datetime as dt

from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, exceptions
from app.utils import get_elapsed
from app.services.image_service import RawImage
from app.services.token_service import create_token, is_valide_token


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
    _token = db.Column(db.String(128), default="")

    avatar = db.relationship("UserAvatar", uselist=False, backref="user")
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

    @property
    def elapsed(self):
        return get_elapsed(self.registered)

    @property
    def token(self):
        if not is_valide_token(self._token):
            self._token = create_token({"sub": self.id})
            super().update()
        return self._token

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
    def get_similar(text: str, page: int):
        return User.query.filter(
            User.username.like(f"%{text}%") | User.id.like(f"%{text}%")
        ).paginate(page=page, per_page=5)

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
        raw_image = RawImage.from_wtf_file(form.avatar.data)
        raw_image.raise_for_image_validity()
        raw_image.crop_to_64square()

        user = User.create_and_get(
            username=form.username.data,
            email=form.email.data,
            password_hash=form.password.data,
        )
        UserAvatar.from_raw_image(raw_image, user)
        return user

    @staticmethod
    def authorize_from_form_and_get(form):
        username = form.username.data
        password = form.password.data
        user = User.get_by_username(username)
        if user is None or not user.check_password(password):
            raise exceptions.AuthorizationError("Incorrect username or password")
        return user

    def update_from_form(self, form):
        self.update_from_data(
            username=form.username.data,
            email=form.email.data,
            password_hash=form.password.data,
            password_changed=form.password.data,
        )

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
    def from_raw_image(raw_image: RawImage, user: User):
        UserAvatar.create(
            b64string=raw_image.b64string,
            mimetype=raw_image.mimetype,
            user=user)


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
    def get_best(return_query=False):
        sub = db.session.query(
            posts_likes.c.post_id,
            func.count(posts_likes.c.user_id).label("count")
        ).group_by(posts_likes.c.post_id) \
         .subquery()

        posts = db.session.query(Post, sub.c.count) \
            .outerjoin(sub, Post.id == sub.c.post_id) \
            .order_by(db.desc("count"))

        # remove count attribute
        if not return_query:
            posts = map(lambda pair: pair[0], posts.all())
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

        raw_image = RawImage.from_wtf_file(form.image.data)
        raw_image.raise_for_image_validity()

        post = Post.create_and_get(
            title=form.title.data,
            body=form.content.data,
            author=author,
            group=group,
        )
        PostImage.from_raw_image(raw_image, post)

    def get_comments(self, query_params: dict):
        sort_comments_by = query_params.get("sort", "popular")
        reverse = bool(query_params.get("reverse", False))
        if sort_comments_by not in ("date", "popular"):
            raise exceptions.IncorrectQueryParam("Incorrect query param: 'sort'")
        if sort_comments_by == "date":
            return sorted(
                self.comments, key=lambda c: c.timestamp, reverse=reverse)
        elif sort_comments_by == "popular":
            return sorted(
                self.comments, key=lambda c: len(c.likes), reverse=reverse)

    @staticmethod
    def get_similar(text: str, page: int):
        posts = Post.get_best(return_query=True)
        return posts.filter(Post.title.like(f"%{text}%") | Post.body.like(
            f"%{text}%") | Post.id.like(f"%{text}%")
        ).paginate(page=page, per_page=5)

    def on_like_click(self, user: User):
        if user in self.likes:
            self.likes.remove(user)
        else:
            self.likes.append(user)
        self.update()


class PostImage(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    b64string = db.Column(db.String)
    mimetype = db.Column(db.String(16))

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    @staticmethod
    def from_raw_image(raw_image: RawImage, post: Post):
        PostImage.create(
            b64string=raw_image.b64string,
            mimetype=raw_image.mimetype,
            post=post)


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

    @staticmethod
    def create_from_form_and_get(form, admin: User):
        if not Group.is_unique_name(form.name.data):
            raise exceptions.NotUniqueGroupName(
                f"Group name '{form.name.data}' is not unique")

        raw_image = RawImage.from_wtf_file(form.logo.data)
        raw_image.raise_for_image_validity()
        raw_image.crop_to_64square()

        group = Group(
            name=form.name.data,
            description=form.description.data
        )
        group.subscribers.append(admin)
        group.update()

        GroupLogo.from_raw_image(raw_image, group)
        return group

    def on_subscribe_click(self, user: User):
        if user in self.subscribers:
            self.subscribers.remove(user)
        else:
            self.subscribers.append(user)
        self.update()

    @staticmethod
    def get_similar(text: str, page: int):
        return Group.query.filter(Group.name.like(f"%{text}%") | Group.id.like(
            f"%{text}%") | Group.description.like(f"%{text}%")).paginate(
            page=page, per_page=5)


class GroupLogo(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    b64string = db.Column(db.String)
    mimetype = db.Column(db.String(16))

    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    @staticmethod
    def from_raw_image(raw_image: RawImage, group: Group):
        GroupLogo.create(
            b64string=raw_image.b64string,
            mimetype=raw_image.mimetype,
            group=group)


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

    def on_like_click(self, user: User):
        if user in self.likes:
            self.likes.remove(user)
        else:
            self.likes.append(user)
        self.update()
