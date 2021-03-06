from flask import jsonify, g, request, url_for

from flask_login import current_user

from . import api
from .errors import forbidden
from .. import db
from ..models import Post


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        prev = url_for('api.get_posts', page=page+1)
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "prev_url": prev,
        "next_url": next,
        "count": pagination.total
        })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.user_id = g.current_user.id
    print(post)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {"Location": url_for('api.get_post', id=post.id)}


@api.route('/posts/<int:id>', methods=['PUT'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user.id != post.user_id:
        return forbidden('Insufficient permissions')
    post.content = request.json.get('content', post.content)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
