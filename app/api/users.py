from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from ..models import User
from .schemas import UserModel, UserModelCreate, UserModelUpdate
from ..utils import token_required


class UsersResource(Resource):
    @token_required
    def get(self, username: str, payload):
        user = self.get_user_or_404(username)
        user_model = UserModel.from_orm(user)
        return jsonify({
            "users": [user_model.dict(exclude={"password_hash"})],
            "status": 200, "ok": True
        })

    @token_required
    def put(self, username: str, payload):
        user = self.get_user_or_404(username)
        self.validate_token(user.id, payload)
        try:
            user_model = UserModelUpdate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            for key, value in user_model:
                if value is not None:
                    setattr(user, key, value)
            user.update(password_changed=user_model.password_hash is not None)
            return jsonify({"ok": True, "status": 201})

    @token_required
    def delete(self, username: str, payload):
        user = self.get_user_or_404(username)
        self.validate_token(user.id, payload)
        user.delete()
        return jsonify({"ok": True, "status": 204})

    def get_user_or_404(self, username: str) -> User:
        user = User.get_by_username(username)
        if not user:
            abort(404, status=404, ok=False,
                  detail=f"User with username {username} not found")
        return user

    def validate_token(self, user_id: int, payload):
        if user_id != payload.get("sub", -1):
            abort(403, status=403, ok=False, detail="Invalid token supplied")


class UsersListResource(Resource):
    @token_required
    def get(self, payload):
        # query параметры, передаваемые в запрос
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 10)
        users = User.get_all(offset, limit)
        if not users:
            abort(400, status=400, ok=False,
                  detail="Wrong offset or limit value")
        return jsonify({
            "users": [UserModel.from_orm(user).dict(exclude={"password_hash"})
                      for user in users],
            "status": 200, "ok": True
        })

    def post(self):
        try:
            user_model = UserModelCreate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            User.create(**user_model.dict())
            return jsonify({"ok": True, "status": 201})
