# -*- coding: utf-8 -*-
"""
    mailproc.transports.file_sender_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the file sender transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import datetime
import random
import string

import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import logging
from email import generator

from mailproc.transports import BaseSenderTransport


class FileSenderTransport(BaseSenderTransport):
    """
    File Sender Transport. This class is mostly intended for testing proposes
    but you are encouraged to find a different use for it :)

    :param directory: Directory path for saving raw emails in file system.
    """

    def __init__(self, directory, **kwargs):
        self.directory = directory

    def connect(self, **kwargs):
        pass

    def close(self):
        pass

    def send_mail(self, email_from, email_to, email_subject, email_text, email_html=None, email_bcc=None,
                  email_encode='utf-8', log=None, json_attachment=None, json_attachment_filename='attachment.json',
                  json_attachment_base64_encode=False, json_attachment_gzip=False, **kwargs):
        """
        Save an email message with text only or multipart HTML body in `directory`
        constructor parameter path

        :param email_from: 'From' email address
        :param email_to:  Email 'To' address, List of string also allowed
        :param email_subject: Email subject
        :param email_text: Text only mail body
        :param email_html: HTML mail body
        :param email_bcc: List of Blind Carbon Copy (BCC) addresses
        :param email_encode: Email encode (default utf-8)
        :param log: Log message (default None)
        :param json_attachment: JSON Object to send as a JSON attachment file
        :param json_attachment_filename: JSON attachment filename (default attachment.json)
        :param json_attachment_base64_encode: Apply a base64 encode to JSON file (default False)
        :param json_attachment_gzip: Send JSON attachment as gzip file (default False)
        """
        if isinstance(email_to, str):
            email_to = [email_to]
        if not log:
            log = email_to
        try:

            msg_root = self.create_message(email_from, email_to, email_subject, email_text, email_html=email_html,
                                           email_bcc=email_bcc, email_encode=email_encode,
                                           json_attachment=json_attachment,
                                           json_attachment_filename=json_attachment_filename,
                                           json_attachment_base64_encode=json_attachment_base64_encode,
                                           json_attachment_gzip=json_attachment_gzip)

            right_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            email_path = os.path.join(self.directory, right_now + "_" + random_str) + ".eml"
            with open(email_path, 'w') as outfile:
                gen = generator.Generator(outfile)
                gen.flatten(msg_root)

            logging.info('SEND {0}'.format(log))
            return True

        except Exception as e:
            logging.error("SEND FAIL {0}. {1}".format(log, e))
            return False
