from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from ..models import Group
from .schemas import GroupModel, GroupModelCreate, GroupModelUpdate


class GroupsResource(Resource):
    exclude_fields = {"subscribers": {"__all__": {"password_hash"}}}

    def get(self, group_id: int):
        group = self.get_group_or_404(group_id)
        group_model = GroupModel.from_orm(group)
        return jsonify({
            "groups": [group_model.dict(exclude=self.exclude_fields)],
            "status": 200, "ok": True
        })

    def put(self, group_id: int):
        group = self.get_group_or_404(group_id)
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
            Group.update(group)
            return jsonify({"ok": True, "status": 201})

    def delete(self, group_id: int):
        group = self.get_group_or_404(group_id)
        Group.delete(group)
        return jsonify({"ok": True, "status": 204})

    def get_group_or_404(self, group_id: int) -> Group:
        group = Group.get_by_id(group_id)
        if not group:
            abort(404, status=404, ok=False,
                  detail=f"Group with id {group_id} not found")
        return group


class GroupsListResource(Resource):
    exclude_fields = {"subscribers": {"__all__": {"password_hash"}}}

    def get(self):
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

    def post(self):
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
