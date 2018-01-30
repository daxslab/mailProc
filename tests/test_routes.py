# -*- coding: utf-8 -*-
import email
import os

from mailproc import Email


def test_from_routes(app, static_dir):
    global count_from
    count_from = 0

    msg = email.message_from_file(open(os.path.join(static_dir, 'test_email.eml')))
    msg.__class__ = Email

    @app.route_from('<name>@test.com')
    def from_trigger(name, mail):
        global count_from
        count_from += 1
        assert name == "test"
        assert mail.get_from_address() == "test@test.com"

    app.run([msg])
    assert count_from == 1

def test_subject_routes(app, static_dir):
    global count_subject
    count_subject = 0

    msg = email.message_from_file(open(os.path.join(static_dir, 'test_email.eml')))
    msg.__class__ = Email

    @app.route_subject('<name> email')
    def from_trigger(name, mail):
        global count_subject
        count_subject += 1
        assert name == "test"
        assert mail.get_subject() == "test email"

    app.run([msg])
    assert count_subject == 1
