from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError

from ..models import Post
from .schemas import PostModel, PostModelUpdate, PostModelCreate
from ..services.token_service import token_required


class PostsResource(Resource):
    @token_required
    def get(self, post_id: int, payload):
        # аргумент payload(именованный, type=dict) передается декоратором
        post = self.get_post_or_404(post_id)
        post_model = PostModel.from_orm(post)
        return jsonify(
            {"posts": [post_model.dict()], "status": 200, "ok": True}
        )

    @token_required
    def put(self, post_id: int, payload):
        post = self.get_post_or_404(post_id)
        self.validate_token(post, payload)
        try:
            post_model = PostModelUpdate(**request.json)
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
            for key, value in post_model:
                if value is not None:
                    setattr(post, key, value)
            post.update()
            return jsonify({"ok": True, "status": 201})

    @token_required
    def delete(self, post_id: int, payload):
        post = self.get_post_or_404(post_id)
        self.validate_token(post, payload)
        post.delete()
        return jsonify({"ok": True, "status": 204})

    def get_post_or_404(self, post_id: int) -> Post:
        post = Post.get_by_id(post_id)
        if not post:
            abort(
                404,
                status=404,
                ok=False,
                detail=f"Post with id {post_id} not found",
            )
        return post

    def validate_token(self, post, payload):
        if post.author_id != payload.get("sub", -1):
            abort(403, status=403, ok=False, detail="You are not the author")


class PostsListResource(Resource):
    @token_required
    def get(self, payload):
        # query параметры, передаваемые в запрос
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 10)
        posts = Post.get_all(offset, limit)
        if not posts:
            abort(
                400, status=400, ok=False, detail="Wrong offset or limit value"
            )
        return jsonify(
            {
                "posts": [PostModel.from_orm(post).dict() for post in posts],
                "status": 200,
                "ok": True,
            }
        )

    @token_required
    def post(self, payload):
        try:
            post_model = PostModelCreate(**request.json)
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
            self.validate_token(post_model.author_id, payload)
            Post.create(**post_model.dict())
            return jsonify({"ok": True, "status": 201})

    def validate_token(self, user_id: int, payload):
        if user_id != payload.get("sub"):
            abort(403, status=403, ok=False, detail="You are not the author")
