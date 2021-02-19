from flask import Flask, render_template


app = Flask(__name__)


LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Cras venenatis vehicula libero et elementum. Sed imperdiet velit "
    "tristique tempor sagittis. Donec sodales diam quam, in tempor dolor "
    "faucibus tempus. Nulla dui erat, ultricies non facilisis non, eleifend "
    "eu felis. Proin vel turpis ante. Suspendisse in odio nec nisi pulvinar "
    "aliquam.".split())

lorem_ipsum = (lambda n: " ".join(LOREM_IPSUM[:n]))


@app.route("/")
def hello():
    return "Hello, World!"


POST_EXAMPLE = {
    "id": 456,
    "author": {"nickname": "bad_user", "id": 5678},
    "title": "Dogs aren't so cute!",
    "elapsed": "1 hour ago",
    "body": lorem_ipsum(20),
    "likes": 1000,
    "comments": 12,
}


@app.route("/template")
def template():
    return render_template("index.html", posts=[POST_EXAMPLE] * 5)


@app.route("/posts/<int:post_id>")
def post(post_id):
    return render_template("post.html", post=POST_EXAMPLE)


if __name__ == '__main__':
    app.run(debug=True)
