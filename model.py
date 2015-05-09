# -*- coding: utf-8 -*-
#
# model.py
#
# Copyright 2014 Carlos Cesar Caballero Diaz <ccesar@linuxmail.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from contrib.pydal import DAL, Field
import datetime
import os


# db = DAL('sqlite://database/storage.sqlite')

SQLITE_FILE = os.path.dirname(os.path.realpath(__file__))+"/database/storage.sqlite"

db = DAL('sqlite://'+SQLITE_FILE)

db.define_table('settings',
                Field('name'),
                Field('value')
                )


def get_setting(setting_name):
    return db(db.settings.name == setting_name).select()


def set_setting(name, value):
    db.settings.update_or_insert(name=name, value=value)

db.define_table('log',
                Field('source'),
                Field('label'),
                Field('value'),
                Field('date', 'datetime', default=datetime.datetime.now())
                )


def add_db_log_entry(source, label, value):
    db.log.insert(source=source, label=label, value=value)
    db.commit()


def get_logs(source=None, label=None):
    if not source and not label:
        query = db.log.source
    elif source and not label:
        query = db.log.source == source
    elif not source and label:
        query = db.log.label == label
    else:
        query = (db.log.source == source) & (db.log.label == label)
    return db(query).select()