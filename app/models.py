import datetime as dt

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    nickname = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(64), unique=True)
    registered = db.Column(db.DateTime, default=dt.datetime.utcnow)
    posts = db.relationship("Post", backref="author")

    @staticmethod
    def get_by_username(username):
        return User.query.filter(User.nickname == username).first()

    @staticmethod
    def is_free_email(email):
        return not db.session.query(
            db.exists().where(User.email == email)).scalar()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def on_delete(user_id):
        GroupsSubscribers.on_user_delete(user_id)
        PostsLikes.on_user_delete(user_id)
        CommentsLikes.on_user_delete(user_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    picture = db.Column(db.LargeBinary, nullable=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    comments = db.relationship("Comment", backref="post")

    @staticmethod
    def get_by_id(post_id):
        return Post.query.filter(Post.id == post_id).first()

    @property
    def beginning(self):
        beginning = " ".join(self.body.split()[:50])
        return f"{beginning}..."
    

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))
    posts = db.relationship("Post", backref="group")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    body = db.Column(db.Text())
    is_reply = db.Column(db.Boolean, default=False)
    reply_to = db.Column(db.Integer, nullable=True) # db.ForeignKey("comment.id")
    # replies = db.relationship("Comment", lazy="dinamic")


class GroupsSubscribers(db.Model):
    __tablename__ = "groups_subscribers"

    primary_key = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)

    @classmethod
    def subscribe(cls, group_id, user_id):
        subscriber = cls(group_id, user_id)
        db.session.add(subscriber)
        db.session.commit()

    @classmethod
    def unsubscribe(cls, group_id, user_id):
        cls.query \
            .filter(cls.group_id == group_id, cls.user_id == user_id) \
            .delete()
        db.session.commit()

    @classmethod
    def on_user_delete(cls, user_id):
        cls.query.filter(cls.user_id == user_id).delete()
        db.session.commit()


class PostsLikes(db.Model):
    __tablename__ = "posts_likes"

    primary_key = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)

    @classmethod
    def add_like(cls, comment_id, user_id):
        like = cls(comment_id, user_id)
        db.session.add(like)
        db.session.commit()

    @classmethod
    def remove_like(cls, comment_id, user_id):
        cls.query \
            .filter(cls.comment_id == comment_id, cls.user_id == user_id) \
            .delete()
        db.session.commit()

    @classmethod
    def on_user_delete(cls, user_id):
        cls.query.filter(cls.user_id == user_id).delete()
        db.session.commit()


class CommentsLikes(db.Model):
    __tablename__ = "comments_likes"

    primary_key = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)

    @classmethod
    def is_liked_by(cls, comment_id, user_id):
        return db.session.query(db.exists()
            .where(cls.comment_id == comment_id, cls.user_id == user_id)
        ).scalar()

    @classmethod
    def add_like(cls, comment_id, user_id):
        like = cls(comment_id, user_id)
        db.session.add(like)
        db.session.commit()

    @classmethod
    def remove_like(cls, comment_id, user_id):
        cls.query \
            .filter(cls.comment_id == comment_id, cls.user_id == user_id) \
            .delete()
        db.session.commit()

    @classmethod
    def on_user_delete(cls, user_id):
        cls.query.filter(cls.user_id == user_id).delete()
        db.session.commit()
