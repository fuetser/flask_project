import datetime as dt

from flask_login import UserMixin
from sqlalchemy.sql.expression import func, extract
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, exceptions
from app.utils import get_elapsed, get_current_time
from app.services.image_service import RawImage
from app.services.token_service import create_token, is_valide_token
from config import Config


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
    _token = db.Column(db.String(256), default="")

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
            db.exists().where(User.email == email)
        ).scalar()

    @staticmethod
    def is_free_username(username: str) -> bool:
        return not db.session.query(
            db.exists().where(User.username == username)
        ).scalar()

    @staticmethod
    def get_similar(text: str, page: int):
        return User.query.filter(User.username.like(f"%{text}%")).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE
        )

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
        raw_image = form.avatar.data
        raw_image.crop_to_64square()
        UserAvatar.from_raw_image(raw_image, user)
        return user

    @staticmethod
    def authorize_from_form_and_get(form):
        username = form.username.data
        password = form.password.data
        user = User.get_by_username(username)
        if user is None or not user.check_password(password):
            raise exceptions.AuthorizationError(
                "Incorrect username or password"
            )
        return user

    def get_posts_from_subscribed_groups(self, page):
        groups_ids = [group.id for group in self.groups]
        return Post.query.filter(Post.group_id.in_(groups_ids)).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE
        )

    def update_from_form(self, form):
        self.update_from_data(
            username=form.username.data,
            email=form.email.data,
            password_hash=form.password.data,
            password_changed=form.password.data,
        )
        if form.image.data:
            raw_image = form.image.data
            raw_image.crop_to_64square()
            UserAvatar.from_raw_image(raw_image, self)

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

    def get_paginated_posts(self, page):
        return Post.query.filter(Post.author_id == self.id).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE, error_out=False
        )

    def get_paginated_subscriptions(self, page):
        groups = [group.id for group in self.groups]
        return Group.query.filter(Group.id.in_(groups)).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE, error_out=False
        )


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
            user=user,
        )


posts_likes = db.Table(
    "posts_likes",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
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
    uses_markdown = db.Column(db.Boolean, default=False)
    likes = db.relationship(
        "User", secondary=posts_likes, backref="post_likes"
    )

    @property
    def elapsed(self):
        return get_elapsed(self.timestamp)

    @staticmethod
    def get_best(page, days=1):
        query = Post.get_best_posts_query()
        current_time = get_current_time() - dt.timedelta(days=days)
        return query.filter(Post.timestamp >= current_time).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE
        )

    @staticmethod
    def get_best_posts_query():
        return (
            Post.query.outerjoin(posts_likes, Post.id == posts_likes.c.post_id)
            .group_by(Post.id)
            .order_by(db.desc(func.count(posts_likes.c.user_id)))
        )

    @staticmethod
    def get_hot(page):
        query = Post.get_hot_posts_query()
        return query.paginate(page=page, per_page=Config.POSTS_PER_PAGE)

    @staticmethod
    def get_hot_posts_query():
        current_time = get_current_time()
        time_limit = current_time - dt.timedelta(hours=1)
        return (
            Post.query.outerjoin(posts_likes, Post.id == posts_likes.c.post_id)
            .group_by(Post.id)
            .filter(Post.timestamp >= time_limit)
            .order_by(
                func.count(posts_likes.c.user_id)
                / (extract("epoch", current_time - Post.timestamp) / 60 + 1)
            )
        )

    @staticmethod
    def from_form(author, group_id, form):
        group = Group.get_by_id(group_id)
        if group is None:
            raise exceptions.GroupDoesNotExists(
                f"Group {group_id} does not exists"
            )

        post = Post.create_and_get(
            title=form.title.data,
            body=form.content.data,
            author=author,
            group=group,
            uses_markdown=form.use_markdown.data,
        )
        if form.image.data is not None:
            raw_image = form.image.data
            PostImage.from_raw_image(raw_image, post)

    def get_comments(self, query_params: dict):
        sort_comments_by = query_params.get("sort", "popular")
        reverse = bool(query_params.get("reverse", False))
        if sort_comments_by not in ("date", "popular"):
            raise exceptions.IncorrectQueryParam(
                "Incorrect query param: 'sort'"
            )
        if sort_comments_by == "date":
            return sorted(
                self.comments, key=lambda c: c.timestamp, reverse=reverse
            )
        elif sort_comments_by == "popular":
            return sorted(
                self.comments, key=lambda c: len(c.likes), reverse=reverse
            )

    @staticmethod
    def get_similar(text: str, page: int):
        query = Post.get_best_posts_query()
        authors = [author.id for author in User.get_similar(text, 1).items]
        return query.filter(
            Post.title.like(f"%{text}%")
            | Post.body.like(f"%{text}%")
            | Post.author_id.in_(authors)
        ).paginate(page=page, per_page=Config.POSTS_PER_PAGE)

    def on_like_click(self, user: User):
        if user in self.likes:
            self.likes.remove(user)
        else:
            self.likes.append(user)
        self.update()

    def update_from_form(self, form):
        self.title = form.title.data
        self.body = form.content.data
        self.uses_markdown = form.use_markdown.data
        if form.image.data:
            raw_image = form.image.data
            raw_image.raise_for_image_validity()
            PostImage.from_raw_image(raw_image, self)
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
            post=post,
        )


groups_subscribers = db.Table(
    "groups_subscribers",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Group(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    logo = db.relationship("GroupLogo", uselist=False, backref="group")
    posts = db.relationship("Post", backref="group")
    subscribers = db.relationship(
        "User", secondary=groups_subscribers, backref="groups"
    )

    @staticmethod
    def is_unique_name(name: str) -> bool:
        return not db.session.query(
            db.exists().where(Group.name == name)
        ).scalar()

    @staticmethod
    def create_from_form_and_get(form, admin: User):
        group = Group(
            name=form.name.data,
            description=form.description.data,
            admin_id=admin.id,
        )
        group.subscribers.append(admin)
        group.update()

        raw_image = form.logo.data
        raw_image.crop_to_64square()
        GroupLogo.from_raw_image(raw_image, group)

        return group

    def on_subscribe_click(self, user: User):
        if user in self.subscribers:
            self.subscribers.remove(user)
        else:
            self.subscribers.append(user)
        self.update()

    def update_from_form(self, form):
        self.name = form.name.data
        self.description = form.description.data
        if form.logo.data:
            raw_image = form.logo.data
            raw_image.crop_to_64square()
            GroupLogo.from_raw_image(raw_image, self)
        self.update()

    def get_paginated_posts(self, page: int):
        return Post.query.filter(Post.group_id == self.id).paginate(
            page=page, per_page=Config.POSTS_PER_PAGE
        )

    @staticmethod
    def get_similar(text: str, page: int):
        return Group.query.filter(
            Group.name.like(f"%{text}%") | Group.description.like(f"%{text}%")
        ).paginate(page=page, per_page=Config.POSTS_PER_PAGE)


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
            group=group,
        )


comments_likes = db.Table(
    "comments_likes",
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Comment(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    body = db.Column(db.Text())
    likes = db.relationship(
        "User", secondary=comments_likes, backref="comment_likes"
    )

    @property
    def elapsed(self):
        return get_elapsed(self.timestamp)

    def on_like_click(self, user: User):
        if user in self.likes:
            self.likes.remove(user)
        else:
            self.likes.append(user)
        self.update()
