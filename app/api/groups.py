from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from ..models import Group
from .schemas import GroupModel, GroupModelCreate, GroupModelUpdate
from ..utils import token_required


class GroupsResource(Resource):
    exclude_fields = {"subscribers": {"__all__": {"password_hash"}}}

    @token_required
    def get(self, group_id: int, payload):
        group = self.get_group_or_404(group_id)
        group_model = GroupModel.from_orm(group)
        return jsonify({
            "groups": [group_model.dict(exclude=self.exclude_fields)],
            "status": 200, "ok": True
        })

    @token_required
    def put(self, group_id: int, payload):
        group = self.get_group_or_404(group_id)
        self.validate_token(group, payload)
        try:
            group_model = GroupModelUpdate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            for key, value in group_model:
                if value is not None:
                    setattr(group, key, value)
            group.update()
            return jsonify({"ok": True, "status": 201})

    @token_required
    def delete(self, group_id: int, payload):
        group = self.get_group_or_404(group_id)
        self.validate_token(group, payload)
        group.delete()
        return jsonify({"ok": True, "status": 204})

    def get_group_or_404(self, group_id: int) -> Group:
        group = Group.get_by_id(group_id)
        if not group:
            abort(404, status=404, ok=False,
                  detail=f"Group with id {group_id} not found")
        return group

    def validate_token(self, group, payload):
        if group.admin_id != payload.get("sub", -1):
            abort(401, status=401, ok=False, detail="Invalid token supplied")


class GroupsListResource(Resource):
    exclude_fields = {"subscribers": {"__all__": {"password_hash"}}}

    @token_required
    def get(self, payload):
        # query параметры, передаваемые в запрос
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 10)
        groups = Group.get_all(offset, limit)
        if not groups:
            abort(400, status=400, ok=False,
                  detail="Wrong offset or limit value")
        return jsonify({
            "groups": [GroupModel.from_orm(group).dict(
                exclude=self.exclude_fields) for group in groups],
            "status": 200, "ok": True
        })

    @token_required
    def post(self, payload):
        try:
            group_model = GroupModelCreate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            Group.create(**group_model.dict())
            return jsonify({"ok": True, "status": 201})

    def validate_token(admin_id, payload):
        if admin_id != payload.get("admin_id", -1):
            abort(401, status=401, ok=False, detail="Invalid token supplied")
