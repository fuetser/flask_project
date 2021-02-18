from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/template")
def template():
    return render_template(
        "index.html",
        posts=[
        {
            "id": 123,
            "author": {"nickname": "cool_user", "id": 1234},
            "title": "Dogs are so cute!",
            "elapsed": "2 hours ago",
        },
        {
            "id": 456,
            "author": {"nickname": "bad_user", "id": 5678},
            "title": "Dogs aren't so cute!",
            "elapsed": "1 hour ago",
        }
        ])
