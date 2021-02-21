from flask import Flask, render_template, request
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
@app.route("/hot")
def wall():
    return render_template("feed.html", posts=[POST_EXAMPLE] * 5)


@app.route("/posts/<int:post_id>")
def post(post_id):
    return render_template("post.html", post=POST_EXAMPLE)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", form=RegisterForm())
    elif request.method == "POST":
        return "Success"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", form=LoginForm())
    elif request.method == "POST":
        return "Success"


if __name__ == '__main__':
    app.run(debug=True)
