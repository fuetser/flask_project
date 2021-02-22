from flask import Flask, render_template, flash, redirect, url_for
from forms import *


app = Flask(__name__)
app.config["SECRET_KEY"] = "some_key_for_now"

LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Cras venenatis vehicula libero et elementum. Sed imperdiet velit "
    "tristique tempor sagittis. Donec sodales diam quam, in tempor dolor "
    "faucibus tempus. Nulla dui erat, ultricies non facilisis non, eleifend "
    "eu felis. Proin vel turpis ante. Suspendisse in odio nec nisi pulvinar "
    "aliquam.".split())

lorem_ipsum = (lambda n: " ".join(LOREM_IPSUM[:n]))

POST_EXAMPLE = {
    "id": 456,
    "author": {"nickname": "bad_user", "id": 5678},
    "title": "Dogs aren't so cute!",
    "elapsed": "1 hour ago",
    "body": lorem_ipsum(20),
    "likes": 1000,
    "comments": 12,
}


@app.route("/best")
def best():
    return render_template("feed.html", posts=[POST_EXAMPLE] * 5,
                           active_link="best")


@app.route("/hot")
def hot():
    return render_template("feed.html", posts=[POST_EXAMPLE] * 10,
                           active_link="hot")


@app.route("/sort")
def sort():
    return render_template("base.html", active_link="sort")


@app.route("/posts/<int:post_id>")
def post(post_id):
    return render_template("post.html", post=POST_EXAMPLE, active_link="hot")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Аккаунт успешно создан!", "success")
        return redirect(url_for("wall"))
    return render_template("register.html", form=form, active_link="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("wall"))
        # flash("Ошибка авторизации!", "danger")
    return render_template("login.html", form=form, active_link="login")


if __name__ == '__main__':
    app.run(debug=True)
