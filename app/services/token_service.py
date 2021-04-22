import datetime as dt
from functools import wraps

from flask_restful import abort, request
import jwt

from config import Config


def validate_token(token: str):
    if not token:
        abort(401, detail="Token is missing", status=401, ok=False)
    try:
        token_data = jwt.decode(
            token, key=Config.SECRET_KEY, algorithms=Config.JWT_ALGORITHM
        )
    except jwt.ExpiredSignatureError:
        abort(401, detail="Token is expired", status=401, ok=False)
    except jwt.InvalidSignatureError:
        abort(401, detail="Token has invalid signature", status=401, ok=False)
    except jwt.DecodeError:
        abort(401, detail="Unable to decode token", status=401, ok=False)
    else:
        return token_data


def is_valide_token(token: str):
    try:
        jwt.decode(
            token, key=Config.SECRET_KEY, algorithms=Config.JWT_ALGORITHM
        )
    except:
        return False
    else:
        return True


def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = request.args.get("token")
        token_data = validate_token(token)
        return func(*args, payload=token_data, **kwargs)

    return inner


def create_token(payload) -> str:
    now = dt.datetime.utcnow()
    payload["iat"] = now
    payload["exp"] = now + dt.timedelta(seconds=Config.TOKEN_EXPIRATION)
    return jwt.encode(payload, Config.SECRET_KEY, Config.JWT_ALGORITHM)
