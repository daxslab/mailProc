# -*- coding: utf-8 -*-
"""
    mailproc.transports.imap_idle_receiver_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the imap idle receiver transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import email
import imaplib
import logging

import sys
import threading

import time

from mailproc.transports import ImapReceiverTransport


class ImapIdleReceiverTransport(ImapReceiverTransport):
    """
    IMAP Idle Receiver Transport. This class instances a receiver object for the IMAP
    protocol which uses the IMAP IDLE check for obtaining new emails

    :param server: Server for establish the IMAP connection
    :param username: Server identifying username
    :param password: Server identifying password
    :param callback: Callback function for processing incoming emails
    :param port: Server port for establish the IMAP connection. Default: None (for standard IMAP port)
    :param use_ssl: Use ssl connection. Default: True
    :param idle_timeout: Timeout for idle connections (in seconds). Default: 8 minutes (60*8)
    :param idle_loop: Restart the IDLE connection when timeout. Default: True
    """

    def __init__(self, server, username, password, callback,
                 port=None, use_ssl=True, idle_timeout=60*8, idle_loop=True, **kwargs):
        super(ImapIdleReceiverTransport, self).__init__(server, username, password, port, use_ssl)

        self.callback = callback
        self.idle_timeout = idle_timeout
        self.connection = None
        self.idle_tag = None
        self.idle_loop = idle_loop

    def get_mails(self, get_msgs_type='(UNSEEN)', mailbox="INBOX", delete=False, **kwargs):
        """
        Starts monitoring an IMAP inbox for incoming emails

        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param mailbox: IMAP mailbox for fetching emails, default: "INBOX"
        :param delete: Delete obtained emails in account (default False)
        """

        self.connection.select(mailbox)

        self._retrieve_mails(self.callback, get_msgs_type=get_msgs_type, delete=delete)

        self._start_idle()

        timeout_tread = threading.Thread(target=self._idle_timeout)
        timeout_tread.setDaemon(True)
        timeout_tread.start()

        line = b""
        idle_finish = b'OK Idle completed.'

        while True and (self.idle_loop or line.endswith(idle_finish)):
            if line.endswith(idle_finish):
                logging.info("restarting idle...")
                line = b""
                self._start_idle()
                continue
            line = self.connection.readline().strip()
            if line.startswith('* BYE '.encode()) or (len(line) == 0):
                logging.info("leaving...")
                break
            if line.endswith('EXISTS'.encode()):
                logging.info("NEW MAIL ARRIVED!")
                self.connection.send('DONE\r\n'.encode())

                self._retrieve_mails(self.callback, get_msgs_type=get_msgs_type, delete=delete)
                self._start_idle()
                # idle_command = "{0} IDLE\r\n".format(self.connection._new_tag().decode())
                # self.connection.send(idle_command.encode())

    def _start_idle(self):
        """
        Starts an IDLE connection
        """
        self.idle_tag = self.connection._new_tag().decode()
        idle_command = "{0} IDLE\r\n".format(self.idle_tag)

        self.connection.send(idle_command.encode())
        logging.info("waiting for new mail...")

    def _idle_timeout(self):
        """
        Thread for timing out an IDLE connection

        """
        while True:
            time.sleep(self.idle_timeout)
            self.connection.send('DONE\r\n'.encode())

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

    def close(self):
        """
        Close current IMAP connection
        """
        # IMAP connection may be closed
        try:
            self.connection.close()
        except imaplib.IMAP4.abort:
            pass  # do nothing if connection is closed
        self.connection.logout()
        logging.info('IMAP connection to {0} for {1} closed'.format(self.server, self.username))
