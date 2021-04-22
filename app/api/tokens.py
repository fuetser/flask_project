from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError
from werkzeug.security import check_password_hash

from ..models import User
from .schemas import TokenCreateModel
from ..services.token_service import create_token


class TokenResource(Resource):
    def post(self):
        try:
            token_model = TokenCreateModel(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(
                400,
                status=400,
                ok=False,
                detail=f"At {error['loc'][0]}: {error['msg']}",
            )
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            user = self.get_user_or_404(token_model.username)
            if check_password_hash(user.password_hash, token_model.password):
                return jsonify(
                    {
                        "token": create_token({"sub": user.id}),
                        "ok": True,
                        "status": 201,
                    }
                )
            abort(
                401, status=401, ok=False, detail="Wrong username or password"
            )

    def get_user_or_404(self, username: str) -> User:
        user = User.get_by_username(username)
        if not user:
            abort(
                404,
                status=404,
                ok=False,
                detail=f"User with username {username} not found",
            )
        return user
