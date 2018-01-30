# -*- coding: utf-8 -*-
"""
    mailproc.transports.base_receiver_transport
    ~~~~~~~~~~~~~~~~~
    This module implements the base class for mailProc receiver transports

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
from abc import abstractmethod
from abc import ABCMeta


class BaseReceiverTransport:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_mails(self):
        pass
