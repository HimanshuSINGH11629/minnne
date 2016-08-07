#!/usr/bin/env python
# -*- coding: utf-8 -*-


from app import db
from datetime import datetime
from slugify import slugify
import arrow
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from flask_login import UserMixin


class Event (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    slug = db.Column(db.String, nullable=False, unique=True, index=True)  # FIXME: Events with the same slug
    description = db.Column(db.String())
    starting_at = db.Column(db.DateTime, nullable=False)
    ending_at = db.Column(db.DateTime, nullable=True)
    price = db.Column(db.Float)
    starred = db.Column(db.Boolean)
    where = db.Column(db.String(255))
    where_link = db.Column(db.String())
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __setattr__(self, key, value):
        if key == 'name':
            idx = 0
            slug = slugify(value)
            while Event.query.filter_by(slug=slug).first():
                idx += 1
                slug = slug + '-' + str(idx)
            self.slug = slug
        super(Event, self).__setattr__(key, value)

    @property
    def short_description(self):
        return "short_description"

    @staticmethod
    def get_upcoming():
        events = Event.query\
            .filter(Event.starting_at > datetime.utcnow())\
            .order_by(Event.starting_at)\
            .limit(5)\
            .all()
        return events

    @staticmethod
    def get_passed():
        events = Event.query\
            .filter(Event.starting_at < datetime.utcnow())\
            .order_by(Event.starting_at.desc())\
            .limit(5)\
            .all()
        return events

    @staticmethod
    def user_events(user):
        events = Event.query\
            .filter(Event.owner_id == user.id)\
            .order_by(Event.starting_at)\
            .all()
        return events

    @property
    def starting_at_hum(self):
        return arrow.get(self.starting_at).humanize()

    def __repr__(self):
        return '<Event %r>' % self.name


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32))
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    reset_password_token = db.Column(db.String(100))
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    firstname = db.Column(db.String(100), nullable=False, default='')
    lastname = db.Column(db.String(100), nullable=False, default='')
    created = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('Event', backref='owner', lazy='dynamic')
    connections = db.relationship('Connection', backref='user', lazy='dynamic')

    def __setattr__(self, key, value):
        if key == 'password':
            self.__dict__[key] = generate_password_hash(value)
        elif key == 'username':
            self.__dict__[key] = value
            self.uuid = str(uuid4()).replace('-', '')
        else:
            super(User, self).__setattr__(key, value)

    def check_password(self, passwd):
        return check_password_hash(self.password, passwd)


class Connection (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    connected = db.Column(db.DateTime, default=datetime.utcnow)


