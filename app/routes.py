from flask import render_template, flash, redirect, url_for, abort, request
from flask.json import jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import app
from app.forms import *
from app.models import *
from app.utils import *


@app.route("/")
@app.route("/best")
def best():
    posts = Post.get_best()
    return render_template("feed.html", posts=posts, active_link="best",
                           current_user=current_user)


@app.route("/hot")
def hot():
    posts = Post.get_hot()
    return render_template("feed.html", posts=posts, active_link="hot",
                           current_user=current_user)


@app.route("/sort")
def sort():
    return render_template("base.html", active_link="sort")


@app.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get(post_id)
    sort = request.args.get("sort", "popular")
    reverse = bool(request.args.get("reverse", False))
    if sort == "date":
        comments = post.get_comments_by_date(reverse=reverse)
    elif sort == "popular":
        comments = post.get_comments_by_likes(reverse=reverse)
    else:
        abort(404)

    if post is not None:
        return render_template("post.html", post=post,
                               current_user=current_user, comments=comments)
    else:
        abort(404)


@app.route("/users/<int:user_id>")
def user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        return render_template("user.html", user=user)
    else:
        abort(404)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        user = User.get_by_username(username)
        is_free_email = User.is_free_email(email)

        if user is None and is_free_email:
            user = User(email=email, username=username)
            password = form.password.data
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash("Аккаунт успешно создан!", "success")
            return redirect(url_for("best"))

        else:
            flash("Аккаунт с такой почтой или именем уже существует!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html", form=form, active_link="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("best"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get_by_username(username)
        if user is not None and user.check_password(password):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("best"))
        else:
            flash("Ошибка авторизации!", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, active_link="login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("best"))


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def create_new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        group_id = request.args.get("group_id")
        if group_id is None:
            abort(404)
        group = Group.get_by_id(group_id)
        post = Post.create_and_get(
            title=form.title.data,
            body=form.content.data,
            author=current_user,
            group=group,
        )

        if form.image.has_file():
            image_bytes = convert_wtf_file_to_bytes(form.image.data)
            try:
                check_image_validity(image_bytes)
            except Exception as e:
                ...
            else:
                mimetype = get_mimetype_from_wtf_file(form.image.data)
                PostImage.from_bytes(image_bytes, mimetype, post)

        return redirect(url_for("group", group_id=group_id))

    return render_template("new_post.html", form=form)


@app.route("/group/<int:group_id>")
def group(group_id):
    group = Group.query.get(group_id)
    if group is not None:
        return render_template(
            "group.html", group=group, current_user=current_user)
    else:
        abort(404)


@app.route("/subscribe/<int:group_id>", methods=["POST"])
def subscribe(group_id):
    group = Group.query.get(group_id)
    if group is not None:
        if current_user in group.subscribers:
            group.subscribers.remove(current_user)
        else:
            group.subscribers.append(current_user)
        db.session.commit()
        return jsonify({"success": "OK"})
    return jsonify({"error": "Group doesn't exists"})


@app.route("/new_group", methods=["GET", "POST"])
@login_required
def new_group():
    form = NewGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        if Group.is_unique_name(name):
            group = Group(name=name, description=description)
            group.subscribers.append(current_user)
            db.session.add(group)
            db.session.commit()
            flash("Группа успешно создана", "success")
            return redirect(url_for("best"))
        else:
            flash("Данное имя уже занято")
            return redirect(url_for("new_group"))

    return render_template("new_group.html", form=form)


@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found"})
    if current_user in post.likes:
        post.likes.remove(current_user)
    else:
        post.likes.append(current_user)
    post.update()
    return jsonify({"success": "OK"})


@app.route("/comment/<int:post_id>", methods=["POST"])
def create_comment(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)
    text = request.values.get("text")
    Comment.create(post_id=post_id, author_id=current_user.id, body=text)
    return jsonify({"success": "OK"})


@app.route("/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.get_by_id(comment_id)
    if not comment:
        abort(404)
    comment.delete()
    return jsonify({"comments": localize_comments(
        len(Post.get_by_id(comment.post_id).comments))})


@app.route("/like_comment/<int:comment_id>", methods=["POST"])
def like_comment(comment_id):
    comment = Comment.get_by_id(comment_id)
    if not comment:
        abort(404)
    if current_user in comment.likes:
        comment.likes.remove(current_user)
    else:
        comment.likes.append(current_user)
    comment.update()
    return jsonify({"success": "OK"})


@app.route("/token")
@login_required
def view_tokens():
    return render_template(
        "tokens.html", token=create_token({"sub": current_user.id}))
