import datetime as dt
from functools import wraps
from math import floor

from flask import jsonify, request
from flask_restful import abort

import jwt

from config import Config


def get_elapsed(timestamp):
    now = dt.datetime.utcnow()
    delta = now - timestamp
    if delta < dt.timedelta(minutes=1):
        return f"{delta.seconds} секунд назад"
    elif delta < dt.timedelta(hours=1):
        minutes = delta.seconds // 60
        return f"{minutes} минут назад"
    elif delta < dt.timedelta(days=1):
        hours = floor(delta.seconds / 60 / 60)
        return f"{hours} часов назад"
    elif delta < dt.timedelta(weeks=1):
        days = floor(delta.seconds / 60 / 60 / 24)
        return f"{days} дней назад"
    elif delta < dt.timedelta(weeks=4):
        weeks = floor(delta.seconds / 60 / 60 / 24 / 7)
        return f"{weeks} недели назад"
    elif delta < dt.timedelta(days=365):
        months = (now.year - timestamp.year) * 12 + now.month - timestamp.month
        return f"{months} месяцев назад"
    else:
        years = now.year - timestamp.year
        return f"{years} лет назад"


def localize_comments(count):
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} комментарий"
    if count % 10 in (2, 3, 4) and count % 100 // 10 != 1:
        return f"{count} комментария"
    return f"{count} комментариев"


def create_token(payload) -> str:
    now = dt.datetime.utcnow()
    payload["iat"] = now
    payload["exp"] = now + dt.timedelta(seconds=Config.TOKEN_EXPIRATION)
    return jwt.encode(payload, Config.SECRET_KEY, Config.JWT_ALGORITHM)


def validate_token(token: str):
    if not token:
        abort(401, detail="Token is missing", status=401, ok=False)
    try:
        token_data = jwt.decode(
            token, key=Config.SECRET_KEY, algorithms=Config.JWT_ALGORITHM)
    except jwt.ExpiredSignatureError:
        abort(401, detail="Token is expired", status=401, ok=False)
    except jwt.InvalidSignatureError:
        abort(401, detail="Token has invalid signature", status=401, ok=False)
    except jwt.DecodeError:
        abort(401, detail="Unable to decode token", status=401, ok=False)
    else:
        return token_data


def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = request.args.get("token")
        token_data = validate_token(token)
        return func(*args, payload=token_data, **kwargs)
    return inner
