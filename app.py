from flask import Flask, render_template


app = Flask(__name__)


LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Cras venenatis vehicula libero et elementum. Sed imperdiet velit "
    "tristique tempor sagittis. Donec sodales diam quam, in tempor dolor "
    "faucibus tempus. Nulla dui erat, ultricies non facilisis non, eleifend "
    "eu felis. Proin vel turpis ante. Suspendisse in odio nec nisi pulvinar "
    "aliquam.".split())


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/template")
def template():
    return render_template("index.html", posts=[
        {
            "id": 123,
            "author": {"nickname": "cool_user", "id": 1234},
            "title": "Dogs are so cute!",
            "elapsed": "2 hours ago",
            "content": " ".join(LOREM_IPSUM[:25]),
            "likes": 100,
            "comments": 12,
        },
        {
            "id": 456,
            "author": {"nickname": "bad_user", "id": 5678},
            "title": "Dogs aren't so cute!",
            "elapsed": "1 hour ago",
            "content": " ".join(LOREM_IPSUM[:20]),
            "likes": 1000,
            "comments": 12,
        }
    ])


if __name__ == '__main__':
    app.run(debug=True)
