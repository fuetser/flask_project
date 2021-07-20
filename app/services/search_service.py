from app import exceptions
from app.models import Group, User, Post


def search_by_query(request):
    query_args = request.args
    query_values = request.values

    page = query_args.get("page", 1, type=int)
    request_text = query_values.get("request_text")
    search_by = query_values.get("sort")

    if request_text is None or search_by not in ("groups", "users", "posts"):
        raise exceptions.InvalidSearchQuery(
            "Request text is empty or invalid search_by value"
        )

    request_text = request_text.strip().lower()
    if search_by == "groups":
        results = Group.get_similar(request_text, page=page)
    elif search_by == "users":
        results = User.get_similar(request_text, page=page)
    elif search_by == "posts":
        results = Post.get_similar(request_text, page=page)

    return results, search_by, request_text, page
