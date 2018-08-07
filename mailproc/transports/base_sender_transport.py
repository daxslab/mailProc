# -*- coding: utf-8 -*-
"""
    mailproc.transports.base_sender_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the base class for mailProc sender transports

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO
import base64
import json
import gzip
from abc import abstractmethod
from abc import ABCMeta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase


class BaseSenderTransport:
    """
    Base class for mailProc sender transports
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, *args, **kwargs):
        """
        Abstract connect function
        """
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        """
        Abstract close function
        """
        pass

    @abstractmethod
    def send_mail(self, *args, **kwargs):
        """
        Abstract send_mail function
        """
        pass

    def create_message(self, email_from, email_to, email_subject, email_text, email_html=None, email_bcc=None,
                       email_encode='utf-8', json_attachment=None, json_attachment_filename='attachment.json',
                       json_attachment_base64_encode=False, json_attachment_gzip=False):
        """
        Send an email message with text only or multipart HTML body

        :param email_from: 'From' email address
        :param email_to:  Email 'To' address, List of string also allowed
        :param email_subject: Email subject
        :param email_text: Text only mail body
        :param email_html: HTML mail body
        :param email_bcc: List of Blind Carbon Copy (BCC) addresses
        :param email_encode: Email encode (default utf-8)
        :param json_attachment: JSON Object to send as a JSON attachment file
        :param json_attachment_filename: JSON attachment filename (default attachment.json)
        :param json_attachment_base64_encode: Apply a base64 encode to JSON file (default False)
        :param json_attachment_gzip: Send JSON attachment as gzip file (default False)
        """
        msg_root = MIMEMultipart()

        msg_root['Subject'] = email_subject
        msg_root['From'] = email_from
        if isinstance(email_to, str):
            msg_root['To'] = email_to
        else:
            msg_root['To'] = ', '.join(email_to)
        if email_bcc:
            msg_root['Bcc'] = ', '.join(email_bcc)


        if email_html:
            msg_alternative = MIMEMultipart('alternative')
            text = email_text
            html = email_html

            part1 = MIMEText(text, 'plain', email_encode)
            part2 = MIMEText(html, 'html', email_encode)

            msg_alternative.attach(part1)
            msg_alternative.attach(part2)

            msg_root.attach(msg_alternative)

        else:
            msg_root.attach(MIMEText(email_text, 'plain', email_encode))

        if json_attachment:

            json_string = json.dumps(json_attachment)

            if sys.version_info >= (3, 0):
                json_string = json_string.encode(email_encode)

            if json_attachment_base64_encode:
                if sys.version_info >= (3, 0):
                    json_string = base64.encodebytes(json_string)
                else:
                    json_string = base64.encodestring(json_string)
            if json_attachment_gzip:
                if sys.version_info >= (3, 0):
                    out = BytesIO()
                else:
                    out = StringIO()
                f = gzip.GzipFile(fileobj=out, mode="w")
                f.write(json_string)
                f.close()
                out.seek(0)
                json_string = out.read()

                attachment = MIMEBase('application', 'x-gzip')
                attachment.set_payload(json_string)
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment',
                                      filename=json_attachment_filename)
                msg_root.attach(attachment)

            else:
                if sys.version_info >= (3, 0):
                    attachment = MIMEText(json_string.decode(email_encode))
                else:
                    attachment = MIMEText(json_string)
                attachment.add_header('Content-Disposition', 'attachment', filename=json_attachment_filename)
                msg_root.attach(attachment)

        return msg_root
