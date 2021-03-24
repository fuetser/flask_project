from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from .schemas import PostModel, PostModelUpdate, PostModelCreate
from ..models import Post


class PostsResource(Resource):
    def get(self, post_id: int):
        post = self.get_post_or_404(post_id)
        post_model = PostModel.from_orm(post)
        return jsonify({
            "posts": [post_model.dict()],
            "status": 200, "ok": True
        })

    def put(self, post_id: int):
        post = self.get_post_or_404(post_id)
        try:
            post_model = PostModelUpdate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            for key, value in post_model:
                if value is not None:
                    setattr(post, key, value)
            Post.update(post)
            return jsonify({"ok": True, "status": 201})

    def delete(self, post_id: int):
        post = self.get_post_or_404(post_id)
        Post.delete(post)
        return jsonify({"ok": True, "status": 204})

    def get_post_or_404(self, post_id: int) -> Post:
        post = Post.get_by_id(post_id)
        if not post:
            abort(404, status=404, ok=False,
                  detail=f"Post with id {post_id} not found")
        return post


class PostsListResource(Resource):
    def get(self):
        # query параметры, передаваемые в запрос
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 10)
        posts = Post.get_all(offset, limit)
        if not posts:
            abort(400, status=400, ok=False,
                  detail="Wrong offset or limit value")
        return jsonify({
            "posts": [PostModel.from_orm(post).dict() for post in posts],
            "status": 200, "ok": True
        })

    def post(self):
        try:
            post_model = PostModelCreate(**request.json)
        except ValidationError as e:
            error = e.errors()[0]
            abort(400, status=400, ok=False,
                  detail=f"At {error['loc'][0]}: {error['msg']}")
        except Exception:
            abort(400, status=400, ok=False, detail="Bad request")
        else:
            Post.create(**post_model.dict())
            return jsonify({"ok": True, "status": 201})
