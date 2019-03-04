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
def verify_password(email, password):
    if email == '':
        return False
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)
