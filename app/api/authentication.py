from .errors import unauthorized

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed Account')


@auth.error_handler
def auth_error():
    return unauthorized('Invalid Credentials')


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_user = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_user = False
    return user.verify_password(password)


@api.route('/tokens/', methods=['GET', 'POST'])
def get_tokens():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid Credentials')
    return jsonify({"token": g.current_user.generate_auth_token(
        expiration=3600), "expiration": 3600})
