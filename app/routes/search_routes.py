from flask import jsonify, request, render_template

from app import app
from app import exceptions
from app.services import search_service


@app.route("/search")
def search_page():
    """Функция для обработки страницы поиска"""
    return render_template("search.html", active_link="sort")


@app.route("/search", methods=["POST"])
def get_search_results():
    """Функция для получения результатов поиска"""
    try:
        (
            results,
            search_by,
            request_text,
            current_page,
        ) = search_service.search_by_query(request)
    except exceptions.InvalidSearchQuery:
        return jsonify({"ok": False})
    else:
        html_data = render_template(
            "search_results.html",
            results=results,
            search_by=search_by,
            request_text=request_text,
            current_page=current_page,
        )
        return jsonify({"ok": True, "html_data": html_data})
