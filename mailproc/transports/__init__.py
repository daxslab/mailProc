# -*- coding: utf-8 -*-
"""
    mailproc.transports
    ~~~~~~~~~~~~~~~~~~~
    Sender and Receiver transports

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""

from .base_receiver_transport import BaseReceiverTransport
from .base_sender_transport import BaseSenderTransport

from .imap_receiver_transport import ImapReceiverTransport
from .imap_idle_receiver_transport import ImapIdleReceiverTransport

from .smtp_sender_transport import SmtpSenderTransport

from .file_receiver_transport import FileReceiverTransport
from .file_sender_transport import FileSenderTransport