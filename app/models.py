import datetime as dt

from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login
from app.utils import get_elapsed


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(64), unique=True)
    registered = db.Column(db.DateTime, default=dt.datetime.utcnow)
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter(User.username == username).first()

    @staticmethod
    def get_all(offset: int, limit: int):
        return User.query.offset(offset).limit(limit).all()

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
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    def update(self, password_changed=False):
        if password_changed:
            self.set_password(self.password_hash)
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def on_delete(self):
        for group in self.groups:
            group.subscribers.remove(self)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


posts_likes = db.Table(
    "posts_likes",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    picture = db.Column(db.LargeBinary, nullable=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    comments = db.relationship("Comment", backref="post")
    likes = db.relationship(
        "User", secondary=posts_likes, backref="post_likes")

    @staticmethod
    def get_by_id(post_id: int):
        return Post.query.filter(Post.id == post_id).first()

    @property
    def beginning(self):
        beginning = " ".join(self.body.split()[:50])
        return f"{beginning}..."

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
    def get_all(offset: int, limit: int):
        return Post.query.offset(offset).limit(limit).all()

    @staticmethod
    def create(**kwargs):
        post = Post(**kwargs)
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)

    def update(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


groups_subscribers = db.Table(
    "groups_subscribers",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    posts = db.relationship("Post", backref="group")
    subscribers = db.relationship(
        "User", secondary=groups_subscribers, backref="groups")

    @staticmethod
    def is_unique_name(name: str) -> bool:
        return not db.session.query(
            db.exists().where(Group.name == name)).scalar()

    @staticmethod
    def get_by_id(group_id: int):
        return Group.query.filter(Group.id == group_id).first()

    @staticmethod
    def get_all(offset: int, limit: int):
        return Group.query.offset(offset).limit(limit).all()

    @staticmethod
    def create(**kwargs):
        group = Group(**kwargs)
        db.session.add(group)
        db.session.commit()
        db.session.refresh(group)

    def update(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()


comments_likes = db.Table(
    "comments_likes",
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Comment(db.Model):
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
