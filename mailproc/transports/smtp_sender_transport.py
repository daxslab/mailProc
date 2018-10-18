# -*- coding: utf-8 -*-
"""
    mailproc.transports.smtp_sender_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the SMTP sender transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import logging
import smtplib

from mailproc.transports import BaseSenderTransport


class SmtpSenderTransport(BaseSenderTransport):
    """
        SMTP Sender Transport. This class instances a sender object for the SMTP
        protocol

        :param server: Server for establish the SMTP connection
        :param username: Server identifying username
        :param password: Server identifying password
        :param port: Server port for establish the SMTP connection. Default: None (for standard SMTP port)
        :param use_ssl: Use ssl secure connection. Default: True
        :param use_tls: Use tls secure connection. Default: False
        """

    def __init__(self, server, username, password, port=None, use_ssl=True, use_tls=False, **kwargs):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.use_tls = use_tls
        self.connection = None

    def connect(self):
        """
        Starts a new SMTP connection
        """
        make_connection = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        s = make_connection(self.server, self.port) if self.port else make_connection(self.server)

        if self.use_tls:
            s.ehlo()
            s.starttls()
            s.ehlo()

        if self.username:
            s.login(self.username, self.password)
        logging.info('CONNECT SMTP connection to {0} for {1}'.format(self.server, self.username))
        self.connection = s

    def close(self):
        """
        Close current SMTP connection
        """
        self.connection.quit()

    def send_mail(self, email_from, email_to, email_subject, email_text, email_html=None, email_bcc=None,
                  email_encode='utf-8', log=None, json_attachment=None, json_attachment_filename='attachment.json',
                  json_attachment_base64_encode=False, json_attachment_gzip=False, **kwargs):
        """
        Send an email message with text only or multipart HTML body

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
        all_send_addresses = []
        if isinstance(email_to, str):
            email_to = [email_to]
        all_send_addresses += email_to
        if email_bcc:
            all_send_addresses += email_bcc
        if not log:
            log = ', '.join(email_to)
        try:

            msg_root = self.create_message(email_from, email_to, email_subject, email_text, email_html=email_html,
                                           email_bcc=email_bcc, email_encode=email_encode,
                                           json_attachment=json_attachment,
                                           json_attachment_filename=json_attachment_filename,
                                           json_attachment_base64_encode=json_attachment_base64_encode,
                                           json_attachment_gzip=json_attachment_gzip)

            self.connection.sendmail(email_from, all_send_addresses, msg_root.as_string())

            logging.info('SEND {0}'.format(log))
            return True

        except Exception as e:
            logging.error("SEND FAIL {0}. {1}".format(log, e))
            return False
