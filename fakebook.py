import os
import sys
import click

from app import create_dev_app, create_test_app, create_prod_app, db
from app.models import User, Post
from flask_migrate import Migrate

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_dev_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)


@app.cli.command()
def test():
	"""run the unit tests"""
	import unittest
	tests = unittest.TestLoader().discover('test')
	unittest.TextTestRunner(verbosity=2).run(tests)
