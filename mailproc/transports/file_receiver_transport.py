# -*- coding: utf-8 -*-
"""
    mailproc.transports.file_receiver_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the file receiver transport class for mailProc.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import os

from email.parser import Parser

from mailproc.transports import BaseReceiverTransport


class FileReceiverTransport(BaseReceiverTransport):
    """
    File Receiver Transport. This class is mostly intended for testing proposes
    but you are encouraged to find a different use for it :)

    :param directory: Directory path for obtaining raw emails in file system.
    """

    def __init__(self, directory, **kwargs):
        self.directory = directory

    def connect(self, **kwargs):
        pass

    def close(self):
        pass

    def get_mails(self, extension='.eml', delete=False, **kwargs):
        """
        Returns mails stored in `directory` constructor parameter

        :param extension: obtain files with extension (default: ".eml")
        :param delete: Delete obtained emails in directory (default False)
        :return: List of :class:`~email.message.Message` objects
        """

        mails = []

        files = os.listdir(self.directory)

        for filename in files:
            if extension:
                if os.path.splitext(filename)[1] != extension:
                    continue
            file_path = os.path.join(self.directory, filename)
            with open(file_path) as email_file:
                email_content = email_file.read()
                email_parser = Parser()
                email_message = email_parser.parsestr(email_content)
                mails.append(email_message)
            if delete:
                os.unlink(file_path)

        return mails
