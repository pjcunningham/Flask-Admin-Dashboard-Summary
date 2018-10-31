# coding: utf-8
__author__ = 'Paul Cunningham'
__copyright = 'Copyright 2018, Paul Cunningham'

from flask import current_app
from flask.cli import click, with_appcontext
from flask_security.utils import hash_password
from models import db, Role, Project


@click.command('create-database')
@with_appcontext
def create_database():
    import string
    import random

    security = current_app.extensions.get('security')

    db.drop_all()
    db.create_all()

    user_role = Role(name='user')
    super_user_role = Role(name='superuser')
    db.session.add(user_role)
    db.session.add(super_user_role)
    db.session.commit()

    test_user = security.datastore.create_user(
        first_name='Admin',
        email='admin',
        password=hash_password('admin'),
        roles=[user_role, super_user_role]
    )

    first_names = [
        'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
        'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
        'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
    ]
    last_names = [
        'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
        'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
        'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
    ]

    for i in range(len(first_names)):
        tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
        tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
        security.datastore.create_user(
            first_name=first_names[i],
            last_name=last_names[i],
            email=tmp_email,
            password=hash_password(tmp_pass),
            roles=[user_role, ]
        )
    db.session.commit()

    for _ in range(0, 100):
        _cost = random.randrange(1, 1000)
        _project = Project(
            name=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            cost=_cost
        )
        db.session.add(_project)

    db.session.commit()
