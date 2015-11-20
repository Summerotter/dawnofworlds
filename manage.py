#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, OrderTypes
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, OrderTypes=OrderTypes)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    
@manager.command
def deploy():
    from flask.ext.migrate import upgrade
    from app.models import Role, OrderTypes
    
    #migrate to latest revision
    upgrade()
    
    #user roles and order tpyes
    Role.insert_roles()
    OrderTypes.insert_orders()


if __name__ == '__main__':
    manager.run()
