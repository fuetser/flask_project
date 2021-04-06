from base64 import b64encode
import datetime as dt
from functools import wraps
from io import BytesIO
from math import floor

from flask_restful import abort, request
import jwt
from PIL import Image
from werkzeug.datastructures import FileStorage

from app import exceptions
from config import Config


def get_elapsed(timestamp):
    now = dt.datetime.utcnow()
    delta = now - timestamp
    seconds = delta.total_seconds()
    if delta < dt.timedelta(minutes=1):
        return f"{floor(seconds)} секунд назад"
    elif delta < dt.timedelta(hours=1):
        minutes = floor(seconds / 60)
        return f"{minutes} минут назад"
    elif delta < dt.timedelta(days=1):
        hours = floor(seconds / 60 / 60)
        return f"{hours} часов назад"
    elif delta < dt.timedelta(weeks=1):
        days = floor(seconds / 60 / 60 / 24)
        return f"{days} дней назад"
    elif delta < dt.timedelta(weeks=4):
        weeks = floor(seconds / 60 / 60 / 24 / 7)
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


def convert_wtf_file_to_bytes(wtf_file: FileStorage):
    with BytesIO() as buffer:
        wtf_file.save(buffer)
        return buffer.getvalue()


def raise_for_image_validity(image_bytes: bytes):
    with BytesIO() as buffer:
        buffer.write(image_bytes)
        try:
            image = Image.open(buffer)
        except:
            raise ValueError("Invalid image content")
        assert check_image_ratio(image), "Image ratio must be 2:1 or bigger"


def check_image_ratio(image: Image):
    width, height = image.size
    return width / height >= 2


def convert_bytes_to_b64string(image: bytes) -> str:
    return b64encode(image).decode("u8")


def get_mimetype_from_wtf_file(wtf_file: FileStorage):
    return wtf_file.mimetype


def check_group_logo_validity(image_bytes: bytes):
    with BytesIO() as buffer:
        buffer.write(image_bytes)
        try:
            image = Image.open(buffer)
        except:
            raise ValueError("Invalid image content")
        assert check_group_logo_image_size(image),\
            "Group logo must be 64x64 or lower"
        assert check_group_logo_have_same_side_sizes(image),\
            "Group logo must have same side sizes"


def check_group_logo_have_same_side_sizes(logo: Image):
    width, height = logo.size
    return width == height


def check_group_logo_image_size(logo: Image):
    width, height = logo.size
    return width <= 64 and height <= 64
