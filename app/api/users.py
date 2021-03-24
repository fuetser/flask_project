from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from ..models import User
from .schemas import UserModel, UserModelCreate, UserModelUpdate


class UsersResource(Resource):
    def get(self, username: str):
        user = self.get_user_or_404(username)
        user_model = UserModel.from_orm(user)
        return jsonify({
            "users": [user_model.dict(exclude={"password_hash"})],
            "status": 200, "ok": True
        })

    def put(self, username: str):
        user = self.get_user_or_404(username)
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
            User.update(
                user, password_changed=user_model.password_hash is not None)
            return jsonify({"ok": True, "status": 201})

    def delete(self, username: str):
        user = self.get_user_or_404(username)
        User.delete(user)
        return jsonify({"ok": True, "status": 204})

    def get_user_or_404(self, username: str) -> User:
        user = User.get_by_username(username)
        if not user:
            abort(404, status=404, ok=False,
                  detail=f"User with username {username} not found")
        return user


class UsersListResource(Resource):
    def get(self):
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
