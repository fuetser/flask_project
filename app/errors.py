from flask import render_template

from app import app


@app.errorhandler(403)
def error403(error):
    return render_template("errors/error403.html"), 403


@app.errorhandler(404)
def error404(error):
    return render_template("errors/error404.html"), 404


@app.errorhandler(500)
def error500(error):
    return render_template("errors/error500.html"), 500
