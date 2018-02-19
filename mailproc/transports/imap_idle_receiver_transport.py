# -*- coding: utf-8 -*-
"""
    mailproc.transports.imap_idle_receiver_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the imap idle receiver transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import email
import logging

import sys

from mailproc.transports import ImapReceiverTransport


class ImapIdleReceiverTransport(ImapReceiverTransport):
    """
    .. warning:: Experimental

    IMAP Idle Receiver Transport. This class instances a receiver object for the IMAP
    protocol which uses the IMAP IDLE check for obtaining new emails

    :param server: Server for establish the IMAP connection
    :param username: Server identifying username
    :param password: Server identifying password
    :param port: Server port for establish the IMAP connection. Default: None (for standard IMAP port)
    :param use_ssl: Use ssl connection. Default: True
    """

    def __init__(self, server, username, password, port=None, use_ssl=True):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None

    def get_mails(self, callback, get_msgs_type='(UNSEEN)', mailbox="INBOX", delete=False):
        """
        Starts monitoring an IMAP inbox for incoming emails

        :param callback: Callback function for processing incoming emails
        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param mailbox: IMAP mailbox for fetching emails, default: "INBOX"
        :param delete: Delete obtained emails in account (default False)
        """

        self.connection.select(mailbox)

        self._retrieve_mails(callback, get_msgs_type=get_msgs_type, delete=delete)

        idle_command = "{0} IDLE\r\n".format(self.connection._new_tag().decode())

        self.connection.send(idle_command.encode())
        logging.info("waiting for new mail...")

        while True:
            line = self.connection.readline().strip()
            if line.startswith('* BYE '.encode()) or (len(line) == 0):
                logging.info("leaving...")
                break
            if line.endswith('EXISTS'.encode()):
                logging.info("NEW MAIL ARRIVED!")
                self.connection.send('DONE\r\n'.encode())

                self._retrieve_mails(callback, get_msgs_type=get_msgs_type, delete=delete)
                idle_command = "{0} IDLE\r\n".format(self.connection._new_tag().decode())
                self.connection.send(idle_command.encode())



    def _retrieve_mails(self, callback, get_msgs_type='(UNSEEN)', delete=False):
        """
        Calls a callback function for new (unseen) mails from account

        :param callback: Callback function for processing incoming emails
        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param delete: Delete obtained emails in account (default False)
        """

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
            if delete:
                self.connection.store(e_id, '+FLAGS', '\\Deleted')
        if delete:
            self.connection.expunge()

        callback(mails)
