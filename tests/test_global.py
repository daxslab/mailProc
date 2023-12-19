# -*- coding: utf-8 -*-
import os
from tempfile import mkdtemp

from mailproc import Email
from mailproc.transports import FileSenderTransport, FileReceiverTransport

TMP_DIR = mkdtemp()


def test_send(app):
    sender_transport = FileSenderTransport(TMP_DIR)
    sender_transport.send_mail(
        "test.user@test.mailproc.cu",
        "noreply@test.mailproc.cu",
        "hello world",
        "the body",
    )

    sender_transport.send_mail(
        "test.user2@test.mailproc.cu",
        "noreply@test.mailproc.cu",
        "this is_my subject",
        "the body",
    )

    assert len(os.listdir(TMP_DIR)) == 2


def test_receive(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)
    assert len(receiver_transport.get_mails()) == 2


def test_run(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)

    global count_from
    count_from = 0
    global subject_hello
    subject_hello = 0
    global subject_this
    subject_this = 0

    @app.route_from('<name>@test.mailproc.cu')
    def testing_from(name, mail):
        global count_from
        count_from += 1
        mail.__class__ = Email
        assert name == mail.get_from_address().split('@')[0]

    @app.route_subject('hello <part>')
    def testing_subject_hello(part, mail):
        global subject_hello
        subject_hello += 1
        mail.__class__ = Email
        assert part == mail.get_subject().split(' ')[1]

    @app.route_subject('this <part> subject')
    def testing_subject_this(part, mail):
        global subject_this
        subject_this += 1
        mail.__class__ = Email
        assert part == mail.get_subject().split(' ')[1]

    app.run(receiver_transport.get_mails(delete=True))

    assert count_from == 2
    assert subject_hello == 1
    assert subject_this == 1
