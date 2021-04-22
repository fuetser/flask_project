import os
import secrets


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres", "postgresql") or "sqlite:///" + os.path.join(basedir, "db.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ALGORITHM = "HS256"
    TOKEN_EXPIRATION = 86400
    POSTS_PER_PAGE = 5
