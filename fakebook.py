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

if os.getenv('FLASK_CONFIG') == 'heroku' \
or os.getenv('FLASK_CONFIG') == 'production':
    app = create_prod_app() 
else:
    app = create_dev_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)


@app.cli.command()
@click.option('--coverage/--no-coverage',  default=False,
              help='Run tests under code coverage')
def test(coverage):
    """run the unit tests"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print(f'HTML version : file://{covdir}/index.html')
        COV.erase()
