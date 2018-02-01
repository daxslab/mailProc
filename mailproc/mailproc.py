# -*- coding: utf-8 -*-
"""
    mailproc.mailproc
    ~~~~~~~~~~~~~~~~~
    This module implements the central application object.

    :copyright: (c) 2018 Daxslab.
    :license: LGPL, see LICENSE for more details.
"""
import copy
from email.message import Message

from .mailproc_email import Email
from .exceptions import MessageInstanceError
from .exceptions import RouteError

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import atexit
import logging
import os
import re
import sys
import tempfile

APP_NAME = "mailproc"
TMP_DIR = os.path.join(tempfile.gettempdir())


class Mailproc:
    """
    The Mailproc object implements an application and acts as the central
    object. It is passed the name of the application. Once it is created
    it will act as a central registry for routes and much more.

    :param name: The name of the mailProc application. This name will be
                 used for identify the current running application.
    """
    def __init__(self, name):
        self.name = name
        self.routes_actions = {
            'from': [],
            'subject': []
        }
        self.set_proc_name(APP_NAME)
        self._at_process_run()

    def _get_pid_file_path(self):
        """
        Returns a PID file path for current application

        :return: PID file path
        """
        return os.path.join(TMP_DIR, "%s-%s.pid" % (self.name, APP_NAME))

    def _create_pid_file(self, pid):
        """
        Creates a PID file

        :param pid: pid value
        :return: created pid file path
        """
        pid_file = self._get_pid_file_path()
        if os.path.isfile(pid_file):
            print("%s already exists, exiting" % pid_file)
            sys.exit(1)
        else:
            open(pid_file, 'w').write(pid)
        return pid_file

    def _at_process_run(self):
        """
        Creates a pid file and register an atexit hook
        """
        pid = str(os.getpid())
        try:
            self._create_pid_file(pid)
        except Exception as e:
            logging.error("Can't create PID file: {0}".format(e))

        atexit.register(self._process_exit)

    def _process_exit(self):
        """
        Removes pid file
        """
        try:
            os.unlink(self._get_pid_file_path())
        except Exception as e:
            logging.error("Can't delete PID file: {0}".format(e))

    @staticmethod
    def set_proc_name(new_name):
        """
        Try to set a system name to the python process

        :param new_name: Process name
        """
        try:
            from ctypes import cdll, byref, create_string_buffer
            if sys.version_info >= (3, 0):
                from ctypes import create_unicode_buffer as create_buffer
            else:
                from ctypes import create_string_buffer as create_buffer
            libc = cdll.LoadLibrary('libc.so.6')
            buff = create_buffer(len(new_name) + 1)
            buff.value = new_name
            libc.prctl(15, byref(buff), 0, 0, 0)
        except Exception as e:
            logging.warning("Can't set process name: {0}".format(e))

    @staticmethod
    def build_route_pattern(route):
        """
        Converts a route pattern to a regular expression

        :param route: Route pattern string
        :return: Compiled regular expression
        """
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{0}$".format(route_regex))

    def route(self, rule, routes_target):
        """
        A decorator that is used to register an action for a given rule and target

        :param rule: Match rule as string
        :param routes_target: Target to be applied the given rule, can be 'from'
                            or 'subject'
        """
        def decorator(f):
            route_pattern = self.build_route_pattern(rule)
            self.routes_actions[routes_target].append((route_pattern, f))
            return f
        return decorator

    def route_from(self, route_str):
        """
        A decorator that is used to register an action for an email "From" address

        :param route_str: Match rule as string
        """
        return self.route(route_str, 'from')

    def route_subject(self, route_str):
        """
        A decorator that is used to register an action for an email subject

        :param route_str: Match rule as string
        """
        return self.route(route_str, 'subject')

    def get_route_match(self, path, in_target):
        """
        Try to find a matching registered action function

        :param path: Route string
        :param in_target: Routes target to find the action. Can be 'from'
                          or 'subject'
        :return: Returns function arguments and action function pair or
                 None if there is no matching actions.
        """
        for route_pattern, action_function in self.routes_actions[in_target]:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), action_function
        return None

    def serve_route(self, path, target, **kwargs):
        """
        Run action functions matching a route path pattern and target

        :param path: Route path string
        :param target: Routes target to find the action. Can be 'from'
                       or 'subject'
        :param kwargs: Additional arguments to pass to the action
        :return: Action function return value
        """
        route_match = self.get_route_match(path, target)
        if route_match:
            route_match_function_kwargs, action_function = route_match
            # join kwargs and route_match_function_kwargs dicts
            kwargs = kwargs.copy()
            kwargs.update(route_match_function_kwargs)

            return action_function(**kwargs)
        else:
            raise RouteError('Route "{0}" has not been registered'.format(path))

    def serve(self, path, in_routes=None, **kwargs):
        if not in_routes:
            in_routes = self.routes_actions.keys()
        for route in in_routes:
            try:
                self.serve_route(path, route, **kwargs)
            except RouteError as e:
                logging.info('{0} for "{1}"'.format(e, route))

    @staticmethod
    def to_mailproc_email(message):
        """
        Return a copy of Message object as a mailproc.Email instance

        :param message: :class:`~email.message.Message` object
        :return: :class:`mailproc.Email` object
        """
        new_message = copy.copy(message)
        new_message.__class__ = Email
        return new_message

    def run(self, mails):
        """
        Apply registered actions to Message objects

        :param mails: A list of :class:`~email.message.Message` objects
        """

        for mail in mails:

            if not isinstance(mail, Message):
                raise MessageInstanceError("run() function requires instances from email.Messge class, found: {0}"
                                           .format(type(mail).__name__))

            steroids_mail = self.to_mailproc_email(mail)

            try:
                self.serve_route(steroids_mail.get_from_address(), 'from', mail=mail)
            except RouteError as e:
                logging.info('{0} for "{1}"'.format(e, 'from'))

            try:
                self.serve_route(steroids_mail.get_subject(), 'subject', mail=mail)
            except RouteError as e:
                logging.info('{0} for "{1}"'.format(e, 'subject'))
