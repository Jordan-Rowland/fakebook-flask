from flask impor Blueprint

api = Blueprint('api', __name__)

from . import authentication, posts, users, comments, errors
