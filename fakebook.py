import os
from app import create_app, db
from app.models import User, Post
from flask_migrate import Migrate

app = create_app('default')
# config_name = 'default'
# app = create_app(config_name)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)
