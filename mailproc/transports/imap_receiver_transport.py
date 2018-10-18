# -*- coding: utf-8 -*-
"""
    mailproc.transports.imap_receiver_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the imap receiver transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import email
import imaplib
import logging

import sys

from mailproc.transports import BaseReceiverTransport


class ImapReceiverTransport(BaseReceiverTransport):
    """
    IMAP Receiver Transport. This class instances a receiver object for the IMAP
    protocol

    :param server: Server for establish the IMAP connection
    :param username: Server identifying username
    :param password: Server identifying password
    :param port: Server port for establish the IMAP connection. Default: None (for standard IMAP port)
    :param use_ssl: Use ssl connection. Default: True
    """

    def __init__(self, server, username, password, port=None, use_ssl=True, **kwargs):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None

    def connect(self, **kwargs):
        """
        Starts a new IMAP connection
        """
        # try:

        make_connection = imaplib.IMAP4_SSL if self.use_ssl else imaplib.IMAP4

        imap_connection = make_connection(self.server, self.port) if self.port else make_connection(self.server)

        imap_connection.login(self.username, self.password)

        logging.info('IMAP connection to {0} for {1} started'.format(self.server, self.username))

        self.connection = imap_connection

        # except Exception as e:
        #     logging.error('IMAP connection to {0} for {1}, {2}'.format(self.imap_server, self.imap_username, e))
        #     return None

    def close(self):
        """
        Close current IMAP connection
        """
        self.connection.close()
        self.connection.logout()
        logging.info('IMAP connection to {0} for {1} closed'.format(self.server, self.username))

    def get_mails(self, get_msgs_type='(UNSEEN)', mailbox="INBOX", delete=False, **kwargs):
        """
        Returns new (unseen) mails from account

        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param mailbox: IMAP mailbox for fetching emails, default: "INBOX"
        :param delete: Delete obtained emails in account (default False)
        :return: List of email.Message objects
        """

        self.connection.select(mailbox)

        # get all unread messages
        status, response = self.connection.search(None, get_msgs_type)
        unread_msg_nums = response[0].split()
        mails = []
        for e_id in unread_msg_nums:
            _, response = self.connection.fetch(e_id, '(RFC822)')
            if sys.version_info >= (3, 0):
                email_message = email.message_from_string(response[0][1].decode('utf-8'))
            else:
                email_message = email.message_from_string(response[0][1])

            mails.append(email_message)

        # Post Process
        for e_id in unread_msg_nums:
            self.connection.store(e_id, '+FLAGS', '\Seen')
            # imap.store(e_id, '+FLAGS', '\Unseen')
            if delete:
                self.connection.store(e_id, '+FLAGS', '\\Deleted')
        if delete:
            self.connection.expunge()

        # # Close connection
        # self.close()

        return mails
