# -*- coding: utf-8 -*-
"""
    mailproc.mailproc_email
    ~~~~~~~~~~~~~~~~~
    This module implements the mailProc email utilities.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO
import sys
import base64
import gzip
import json
import logging

from email.message import Message
from email.header import decode_header
import email


class Email(Message):
    """
    Email utility class. This class is intended to be used as an utility
    class for interacting with :class:`~email.message.Message` objects

    """

    def _walk_email(self):
        for part in self.walk():
            if part.get_content_type() == "multipart/alternative":
                continue
            yield part

    @staticmethod
    def decode_mime_words(s):
        """
        Return a decoded mime header string

        :param s: String to decode
        :return: Decoded string
        """
        return u''.join(
            word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
            for word, encoding in decode_header(s))

    def get_from(self):
        """
        Return the raw 'From' header

        :return: From header string
        """
        return self['From']

    def get_from_address(self):
        """
        Return 'From' header email address

        :return: From email address string
        """
        return email.utils.parseaddr(self.get_from())[1]

    def get_from_name(self, decode=True):
        """
        Return email 'From' header name

        :param decode: If True, try to decode
        :return: Email From header name string
        """
        name = email.utils.parseaddr(self.get_from())[0]
        if decode:
            name = self.decode_mime_words(name)
        return name

    def get_subject(self, decode=True):
        """
        Return email subject

        :param decode: If True, try to decode
        :return: Email subject string
        """
        subject = self['Subject']
        if decode:
            subject = self.decode_mime_words(subject)
        return subject

    def get_body(self, html=False):
        """
        Return Email body

        :param html: Get Email HTML body. Default: False
        :return: Email body
        """
        content_type = "text/plain" if not html else "text/html"
        body = ''
        for part in self._walk_email():
            if part.get_content_type() == content_type:
                body += part.get_payload(decode=1).decode(part.get_content_charset())
        return body

    def get_json_attachment(self, attachment_name=None, attachment_content_type=None,
                            base64_decode=False, gzipped=False, email_encode='utf-8'):
        """
        Return a json object stored in attachment

        :param attachment_name: Name of attachment file to find
        :param attachment_content_type: Content type of attachment file to find
        :param base64_decode: If true looks for a base64 encoded json file
        :param gzipped: If true try to unzip an attachment gzip file
        :param email_encode: Encoding for treat body attachments. Default: 'utf-8'
        :return: Json object stored in email attachment
        """
        if self.get_content_maintype() != 'multipart':
            return False

        for part in self.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            # attachment filename
            filename = part.get_filename()
            if attachment_name and filename != attachment_name:
                continue

            # attachment content type
            content_type = part.get_content_type()
            if attachment_content_type and content_type != attachment_content_type:
                continue

            # attachment decoded body
            body = part.get_payload(decode=True)

            # decompress gzipped file
            if gzipped:
                try:
                    if sys.version_info >= (3, 0):
                        body = gzip.decompress(body)
                    else:
                        infile = StringIO()
                        infile.write(body)
                        f = gzip.GzipFile(fileobj=infile, mode="r")
                        f.rewind()
                        body = f.read()
                except ValueError as e:
                    logging.error('get_json_attachment gzip error: {0}'.format(e))
                    continue

            # decode base64
            if base64_decode:
                body = base64.b64decode(body)

            # check if is a json string
            try:
                if sys.version_info >= (3, 0):
                    return json.loads(body.decode(email_encode))
                else:
                    return json.loads(body)
            except ValueError as e:
                logging.error('get_json_attachment json error: {0}'.format(e))
                continue

        return False
