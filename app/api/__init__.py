from app import api
from .groups import GroupsResource, GroupsListResource
from .posts import PostsResource, PostsListResource
from .users import UsersResource, UsersListResource


api.add_resource(PostsResource, "/posts/<int:post_id>")
api.add_resource(PostsListResource, "/posts")

api.add_resource(UsersResource, "/users/<string:username>")
api.add_resource(UsersListResource, "/users")

api.add_resource(GroupsResource, "/groups/<int:group_id>")
api.add_resource(GroupsListResource, "/groups")
