#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2015 Carlos Cesar Caballero Diaz <ccesar@linuxmail.org>
#   
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import poplib
import imaplib
import email
import os
import sys
import atexit

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imp

from model import *

from smtplib import SMTPRecipientsRefused

APP_NAME = "mailproc"

PID_FILE = os.path.dirname(os.path.realpath(__file__))+"/mailproc.pid"

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/modules")


class mailproc_processor:

    def __init__(self):
        self.set_proc_name(APP_NAME)
        self.process_run()

        # folders
        self.config_folder = os.getenv('HOME')+"/.procmail"
        self.system_module_folder = os.path.dirname(os.path.realpath(__file__))+"/modules"
        self.user_module_folder = self.config_folder+"/modules"
        self.module_folder = [self.system_module_folder, self.user_module_folder]

        # modules main module name
        self.main_module = "__init__"

        # create folders if don't exist
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)
        if not os.path.exists(self.user_module_folder):
            os.makedirs(self.user_module_folder)

    def process_run(self):

        pid = str(os.getpid())
        pid_file = PID_FILE

        if os.path.isfile(pid_file):
            print "%s already exists, exiting" % pid_file
            sys.exit()
        else:
            file(pid_file, 'w').write(pid)


        atexit.register(self.process_exit, pid_file)

    def process_exit(self, pid_file):
        os.unlink(pid_file)


    def set_proc_name(self, new_name):
        """
        Set a system name to the python process
        :param new_name: Process name
        """
        try:
            from ctypes import cdll, byref, create_string_buffer
            libc = cdll.LoadLibrary('libc.so.6')
            buff = create_string_buffer(len(new_name)+1)
            buff.value = new_name
            libc.prctl(15, byref(buff), 0, 0, 0)
        except:
            pass

    def get_modules(self):
        """
        Obtain modules from folders
        :return: List of available modules info
        """
        modules = []
        for folder in self.module_folder:
            possible_modules = os.listdir(folder)
            for i in possible_modules:
                # print i
                location = os.path.join(folder, i)
                if not os.path.isdir(location) or not self.main_module + ".py" in os.listdir(location):
                    continue
                info = imp.find_module(self.main_module, [location])
                modules.append({"name": i, "info": info})
        return modules

    def load_module(self, module):
        """
        Get module main module
        :return: Module main module
        """
        return imp.load_module(self.main_module, *module["info"])

    def call_modules(self):
        """
        Modules callback
        """
        for i in self.get_modules():
            module = self.load_module(i)
            module.run(mailproc())


class mailproc:

    def __init__(self):
        self.db = db

    def get_new_mails(self, module, imap_server, imap_username, imap_password, imap_port=None, use_ssl=True,
                      get_msgs_type='(UNSEEN)', delete=False):
        """
        Returns new unseen mails from account
        :param module: Main module object
        :param imap_server: IMAP server address
        :param imap_username: IMAP account username
        :param imap_password: IMAP account password
        :param imap_port: IMAP server port
        :param use_ssl: Use secure SSL connection (default True)
        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param delete: Delete obtained emails in account (default False)
        :return: List of emails objects
        """
        
        make_connection = imaplib.IMAP4_SSL if use_ssl else imaplib.IMAP4

        # Login to INBOX
        imap = make_connection(imap_server, imap_port) if imap_port else make_connection(imap_server)
        
        imap.login(imap_username, imap_password)
        imap.select('INBOX')

        # get all unread messages
        status, response = imap.search(None, get_msgs_type)
        unread_msg_nums = response[0].split()
        mails = []
        for e_id in unread_msg_nums:
            _, response = imap.fetch(e_id, '(RFC822)')
            # print response
            email_message = email.message_from_string(response[0][1])
            mails.append(email_message)

        # Post Process
        for e_id in unread_msg_nums:            
            imap.store(e_id, '+FLAGS', '\Seen')
            # imap.store(e_id, '+FLAGS', '\Unseen')
            if delete:
                imap.store(e_id, '+FLAGS', '\\Deleted')
        if delete:
            imap.expunge()

        # Close connection
        imap.close()
        imap.logout()
        return mails

    def smpt_connect(self, module, smtp_address, smtp_username=None, smtp_password=None, log=False,
                     smtp_port=None, use_ssl=True):
        """
        Creates a new SMTP connection
        :param module: Main module object
        :param smtp_address: SMTP server address
        :param smtp_username: SMTP username
        :param smtp_password: SMTP password
        :param log: Enable log (default False)
        :param smtp_port: SMTP server port
        :param use_ssl: Use secure SSL connection (default True)
        :return: SMTP connection object
        """
        try:
            make_connection = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
            s = make_connection(smtp_address, smtp_port) if smtp_port else make_connection(smtp_address)
            if smtp_username:
                s.login(smtp_username, smtp_password)
            if log == 'DEBUG':
                self.log(module, 'CONNECT', 'SMTP connection to %s for %s' % (smtp_address, smtp_username))
            return s
        except Exception as e:
            if log:
                self.log(module, 'ERROR', 'SMTP connection to %s for %s, %s' % (smtp_address, smtp_username, e.strerror))
            return None

    def smtp_close(self, module, connection):
        """
        Close given SMTP connection
        :param module: Main module object
        :param connection: SMTP connection object
        """

        connection.quit()

    def pop_connect(self, module, pop_address, pop_username, pop_password, log=False,
                     pop_port=None, use_ssl=True):
        """
        Creates a new POP3 connection
        :param module: Main module object
        :param pop_address: POP3 server address
        :param pop_username: POP3 username
        :param pop_password: POP3 password
        :param log: Enable log (default False)
        :param pop_port: POP3 server port
        :param use_ssl: Use secure SSL connection (default True)
        :return: POP3 connection object
        """
        try:
            make_connection = poplib.POP3_SSL if use_ssl else poplib.POP3
            s = make_connection(pop_address, pop_port) if smtp_port else make_connection(pop_address)
            s.user(pop_username)
            s.pass_(pop_password)
            if log == 'DEBUG':
                self.log(module, 'CONNECT', 'POP3 connection to %s for %s' % (pop_address, pop_username))
            return s
        except Exception as e:
            if log:
                self.log(module, 'ERROR', 'POP3 connection to %s for %s, %s' % (pop_address, pop_username, e.strerror))
            return None

    def pop_close(self, module, connection):
        """
        Close given POP3 connection
        :param module: Main module object
        :param connection: POP3 connection object
        """

        connection.quit()


    def send_email(self, module, smtp_address, email_from, email_to,
                    email_subject, email_text, email_html=None, email_encode='utf-8', log=None,
                    smtp_port=None, smtp_username=None, smtp_password=None, use_ssl=True):
        """
        Send an email message with text only or multipart HTML body
        :param module: Main module object
        :param smtp_address: SMTP server address
        :param email_from:
        :param email_to:
        :param email_subject:
        :param email_text: Text only mail body
        :param email_html: HTML mail body
        :param email_encode: Email encode (default utf-8)
        :param log: Log message (default None)
        :param smtp_port: SMTP server port
        :param smtp_username: SMTP username
        :param smtp_password: SMTP password
        :param use_ssl: Use secure SSL connection (default True)
        """
        try:
            msg = MIMEMultipart('alternative') if email_html else MIMEText(email_text, 'plain', email_encode)

            msg['Subject'] = email_subject
            msg['From'] = email_from
            msg['To'] = email_to

            if email_html:
                text = email_text
                html = email_html

                part1 = MIMEText(text, 'plain', email_encode)
                part2 = MIMEText(html, 'html', email_encode)

                msg.attach(part1)
                msg.attach(part2)

            s = self.smpt_connect(module, smtp_address, smtp_username=smtp_username,
                                  smtp_password=smtp_password, log=True,
                                  smtp_port=smtp_port, use_ssl=use_ssl)

            if not s:
                return

            s.sendmail(email_from, [email_to], msg.as_string())

            if not log:
                log = email_to
            self.log(module, 'SEND', log)

            self.smtp_close(module, s)

        except SMTPRecipientsRefused as e:
            for addresses in e:
                for address in addresses:
                    self.log(module, 'ERROR', 'Rejected sender address %s' % address)
        except Exception as e:
            self.log(module, 'ERROR', 'Error sending email to %s: %s'+e.strerror % email_to)

    def send_two_part_email(self, module, smtp_address, smtp_username, smtp_password, email_from, email_to,
                            email_subject, email_text, email_html, email_encode='utf-8', log=None,
                            smtp_port=None, use_ssl=True):
        """
        Send a multi part email message with text only and HTML body
        :param module: Main module object
        :param smtp_address: SMTP server address
        :param smtp_username: SMTP username
        :param smtp_password: SMTP password
        :param email_from:
        :param email_to:
        :param email_subject:
        :param email_text: Text only mail body
        :param email_html: HTML mail body
        :param email_encode: Email encode (default utf-8)
        :param log: Log message (default None)
        :param smtp_port: SMTP server port
        :param use_ssl: Use secure SSL connection (default True)
        """
        try:

            msg = MIMEMultipart('alternative')

            msg['Subject'] = email_subject
            msg['From'] = email_from
            msg['To'] = email_to

            text = email_text
            html = email_html

            part1 = MIMEText(text, 'plain', email_encode)
            part2 = MIMEText(html, 'html', email_encode)

            msg.attach(part1)
            msg.attach(part2)

            s = self.smpt_connect(module, smtp_address, smtp_username, smtp_password, log=True,
                                  smtp_port=smtp_port, use_ssl=use_ssl)

            if not s:
                return

            s.sendmail(email_from, [email_to], msg.as_string())

            if not log:
                log = email_to
            self.log(module, 'SEND', log)

            self.smtp_close(module, s)

        except Exception as e:
            self.log(module, 'ERROR', 'Error sending two-part email to %s: '+e.strerror % email_to)


    def process(self, module, mails, function):
        """
        Email processing hook, apply a processing function to any email in a list
        :param module: Main module object
        :param mails: List of emails
        :param function: Processing function
        """
        try:
            for mail in mails:

                if module.__module_log__ == 'DEBUG':
                    self.log(module, 'PROCESS', 'Processing function %s on mail %s' % (function.__name__, str(mail)))

                function(mail)

        except Exception as e:
            self.log(module, 'ERROR', 'Processing error: %s' % e.strerror)

    def log(self, module, label, value):
        """
        Adds a new log entry
        :param module: Main module object
        :param label: Log label
        :param value: Log value
        """
        if module.__module_log__ == 'DB':
            add_db_log_entry(module.__module_name__, label, value)
        elif module.log == 'CMD':
            print '%s %s %s' % (module.__module_name__, label, value)


if __name__ == '__main__':
    mailproc_proc = mailproc_processor()
    mailproc_proc.call_modules()
