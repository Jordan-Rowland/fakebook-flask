import os
from app import create_dev_app, create_test_app, create_prod_app, db
from app.models import User, Post
from flask_migrate import Migrate

app = create_dev_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)
