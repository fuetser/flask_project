import datetime as dt

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(64), unique=True)
    registered = db.Column(db.DateTime, default=dt.datetime.utcnow)
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

    @staticmethod
    def get_by_username(username):
        return User.query.filter(User.username == username).first()

    @staticmethod
    def is_free_email(email):
        return not db.session.query(
            db.exists().where(User.email == email)).scalar()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def on_delete(self):
        for group in self.groups:
            group.subscribers.remove(self)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


posts_likes = db.Table("posts_likes",
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
    def get_by_id(post_id):
        return Post.query.filter(Post.id == post_id).first()

    @property
    def beginning(self):
        beginning = " ".join(self.body.split()[:50])
        return f"{beginning}..."


groups_subscribers = db.Table("groups_subscribers",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))
    posts = db.relationship("Post", backref="group")
    subscribers = db.relationship(
        "User", secondary=groups_subscribers, backref="groups")

    @staticmethod
    def is_unique_name(name):
        return not db.session.query(
            db.exists().where(Group.name == name)).scalar()


comments_likes = db.Table("comments_likes",
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
