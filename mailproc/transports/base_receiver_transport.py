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
    """
    Base class for mailProc receiver transports
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self):
        """
        Abstract connect function
        """
        pass

    @abstractmethod
    def close(self):
        """
        Abstract close function
        """
        pass

    @abstractmethod
    def get_mails(self):
        """
        Abstract get_mails function
        """
        pass
