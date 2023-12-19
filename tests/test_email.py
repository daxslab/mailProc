# -*- coding: utf-8 -*-
import os
from tempfile import mkdtemp

from mailproc import Email
from mailproc.transports import FileSenderTransport, FileReceiverTransport

TMP_DIR = mkdtemp()

TEST_JSON = {
    "bool": True,
    'number': 4,
    "string": "this is a string",
    'list': ["one", "two", 'three']}

MAIL_DATA = [
    "test.user@test.mailproc.cu",
    "noreply@test.mailproc.cu",
    "hello world",
    "the body"
]


def test_create_json_email(app):
    sender_transport = FileSenderTransport(TMP_DIR)
    email_sent = sender_transport.send_mail(
        *MAIL_DATA,
        json_attachment=TEST_JSON
    )

    assert email_sent == True


def test_get_json_email(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)
    mail = receiver_transport.get_mails(delete=True)[0]
    mail.__class__ = Email
    json_dict = mail.get_json_attachment()
    assert json_dict == TEST_JSON


def test_create_json_base64_email(app):
    sender_transport = FileSenderTransport(TMP_DIR)
    email_sent = sender_transport.send_mail(
        *MAIL_DATA,
        json_attachment=TEST_JSON,
        json_attachment_base64_encode=True
    )

    assert email_sent == True


def test_get_json_base64_email(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)
    mail = receiver_transport.get_mails(delete=True)[0]
    mail.__class__ = Email
    json_dict = mail.get_json_attachment(base64_decode=True)
    assert json_dict == TEST_JSON


def test_create_json_gzip_email(app):
    sender_transport = FileSenderTransport(TMP_DIR)
    email_sent = sender_transport.send_mail(
        *MAIL_DATA,
        json_attachment=TEST_JSON,
        json_attachment_gzip=True
    )

    assert email_sent == True


def test_get_json_gzip_email(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)
    mail = receiver_transport.get_mails(delete=True)[0]
    mail.__class__ = Email
    json_dict = mail.get_json_attachment(gzipped=True)
    assert json_dict == TEST_JSON


def test_create_json_base64_gzip_email(app):
    sender_transport = FileSenderTransport(TMP_DIR)
    email_sent = sender_transport.send_mail(
        *MAIL_DATA,
        json_attachment=TEST_JSON,
        json_attachment_base64_encode=True,
        json_attachment_gzip=True
    )

    assert email_sent == True


def test_get_json_base64_gzip_email(app):
    receiver_transport = FileReceiverTransport(TMP_DIR)
    mail = receiver_transport.get_mails(delete=True)[0]
    mail.__class__ = Email
    json_dict = mail.get_json_attachment(base64_decode=True, gzipped=True)
    assert json_dict == TEST_JSON
