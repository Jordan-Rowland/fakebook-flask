@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({"posts": [post.to_json() for post in posts]})


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id):
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {"Location": url_for('api.get_post', id=post.id)}
