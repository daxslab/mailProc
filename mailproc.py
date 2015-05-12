#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 Carlos Cesar Caballero Diaz <ccesar@nauta.cu>
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

from contrib.pydal import DAL, Field
import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imp

# from model import *

from smtplib import SMTPRecipientsRefused

APP_NAME = "mailproc"

PID_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mailproc.pid")

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "services"))

__SERVICES_FOLDER__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "services")


class MailProcProcessor:

    def __init__(self):
        self.set_proc_name(APP_NAME)
        self.process_run()

        # folders
        self.config_folder = os.path.join(os.getenv('HOME'), ".procmail")
        # self.system_service_folder = os.path.dirname(os.path.realpath(__file__))+"/services"
        self.system_service_folder = __SERVICES_FOLDER__
        self.user_service_folder = os.path.join(self.config_folder, "services")
        self.service_folder = [self.system_service_folder, self.user_service_folder]

        # services main service name
        self.main_service = "__init__"

        # create folders if don't exist
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)
        if not os.path.exists(self.user_service_folder):
            os.makedirs(self.user_service_folder)

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

    def get_services(self):
        """
        Obtain services from folders
        :return: List of available services info
        """
        services = []
        for folder in self.service_folder:
            possible_services = os.listdir(folder)
            for i in possible_services:
                # print i
                location = os.path.join(folder, i)
                if not os.path.isdir(location) or not self.main_service + ".py" in os.listdir(location):
                    continue
                info = imp.find_module(self.main_service, [location])
                services.append({"name": i, "info": info})
        return services

    def load_service(self, service):
        """
        Get service main service
        :return: Service main service
        """
        return imp.load_module(self.main_service, *service["info"])

    def call_services(self):
        """
        Services callback
        """
        for i in self.get_services():
            service = self.load_service(i)
            # service.run(mailproc())
            service.run()
            # self.load_service(i)


class MailProc:

    def __init__(self):
        self.db = None

        self.__service_log__ = 'CMD'
        self.__service_log_enabled__ = False

        self.__service_name__ = 'Default'

    def set_log_type(self, type):
        """
        Set service log type
        :param type: service log type ('DB', 'CMD', 'file')
        """
        self.__service_log__ = type

    def get_log_type(self):
        """
        Returns service log type
        :return: Log type
        """
        return self.__service_log__

    def enable_log(self):
        self.__service_log_enabled__ = True

    def enable_log_debuging(self):
        self.__service_log_enabled__ = 'DEBUG'

    def disable_log(self):
        self.__service_log_enabled__ = False

    def get_new_mails(self, imap_server, imap_username, imap_password, imap_port=None, use_ssl=True,
                      get_msgs_type='(UNSEEN)', delete=False):
        """
        Returns new unseen mails from account
        :param imap_server: IMAP server address
        :param imap_username: IMAP account username
        :param imap_password: IMAP account password
        :param imap_port: IMAP server port
        :param use_ssl: Use secure SSL connection (default True)
        :param get_msgs_type: Expression for emails to get '(UNSEEN)' by default to get new emails
        :param delete: Delete obtained emails in account (default False)
        :return: List of emails objects
        """

        imap = self.imap_connect(imap_server, imap_username, imap_password, imap_port=imap_port, use_ssl=use_ssl)

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
        self.imap_close(imap)

        return mails

    def imap_connect(self, imap_server, imap_username, imap_password, imap_port=None, use_ssl=True):
        """
        Creates a new IMAP connection
        :param imap_server: IMAP server address
        :param imap_username: IMAP account username
        :param imap_password: IMAP account password
        :param imap_port: IMAP server port
        :param use_ssl: Use secure SSL connection (default True)
        :return: IMAP connection object
        """
        try:

            make_connection = imaplib.IMAP4_SSL if use_ssl else imaplib.IMAP4

            imap_connection = make_connection(imap_server, imap_port) if imap_port else make_connection(imap_server)

            imap_connection.login(imap_username, imap_password)

            if self.__service_log_enabled__ == 'DEBUG':
                self.log('CONNECT', 'IMAP connection to %s for %s' % (imap_server, imap_username))

            return imap_connection
        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'IMAP connection to %s for %s, %s' % (imap_server, imap_username, e.message))
            return None

    def imap_close(self, connection):
        """
        Close an imap connection
        :param connection: IMAP connection object
        """
        connection.close()
        connection.logout()
    
    def smtp_connect(self, smtp_address, smtp_username=None, smtp_password=None,
                     smtp_port=None, use_ssl=True):
        """
        Creates a new SMTP connection
        :param smtp_address: SMTP server address
        :param smtp_username: SMTP username
        :param smtp_password: SMTP password
        :param smtp_port: SMTP server port
        :param use_ssl: Use secure SSL connection (default True)
        :return: SMTP connection object
        """
        try:
            make_connection = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
            s = make_connection(smtp_address, smtp_port) if smtp_port else make_connection(smtp_address)
            if smtp_username:
                s.login(smtp_username, smtp_password)
            if self.__service_log_enabled__ == 'DEBUG':
                self.log('CONNECT', 'SMTP connection to %s for %s' % (smtp_address, smtp_username))
            return s
        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'SMTP connection to %s for %s, %s' % (smtp_address, smtp_username, e.message))
            return None

    def smtp_close(self, connection):
        """
        Close given SMTP connection
        :param service: Main service object
        :param connection: SMTP connection object
        """
        connection.quit()

    def pop_connect(self, pop_address, pop_username, pop_password,
                     pop_port=None, use_ssl=True):
        """
        Creates a new POP3 connection
        :param pop_address: POP3 server address
        :param pop_username: POP3 username
        :param pop_password: POP3 password
        :param pop_port: POP3 server port
        :param use_ssl: Use secure SSL connection (default True)
        :return: POP3 connection object
        """
        try:
            make_connection = poplib.POP3_SSL if use_ssl else poplib.POP3
            s = make_connection(pop_address, pop_port) if pop_port else make_connection(pop_address)
            s.user(pop_username)
            s.pass_(pop_password)
            if self.__service_log_enabled__ == 'DEBUG':
                self.log('CONNECT', 'POP3 connection to %s for %s' % (pop_address, pop_username))
            return s
        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'POP3 connection to %s for %s, %s' % (pop_address, pop_username, e.message))
            return None

    def pop_close(self, service, connection):
        """
        Close given POP3 connection
        :param service: Main service object
        :param connection: POP3 connection object
        """

        connection.quit()


    def send_email(self, smtp_address, email_from, email_to,
                    email_subject, email_text, email_html=None, email_encode='utf-8', log=None,
                    smtp_port=None, smtp_username=None, smtp_password=None, use_ssl=True):
        """
        Send an email message with text only or multipart HTML body
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

            s = self.smtp_connect(smtp_address, smtp_username=smtp_username,
                                  smtp_password=smtp_password,
                                  smtp_port=smtp_port, use_ssl=use_ssl)

            if not s:
                return

            s.sendmail(email_from, [email_to], msg.as_string())

            if not log:
                log = email_to
            self.log('SEND', log)

            self.smtp_close(s)

        except SMTPRecipientsRefused as e:
            if self.__service_log_enabled__:
                for addresses in e:
                    for address in addresses:
                        self.log('ERROR', 'Rejected sender address %s' % address)
        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'Error sending email to %s: %s'+e.message % email_to)

    def send_two_part_email(self, smtp_address, smtp_username, smtp_password, email_from, email_to,
                            email_subject, email_text, email_html, email_encode='utf-8', log=None,
                            smtp_port=None, use_ssl=True):
        """
        Send a multi part email message with text only and HTML body
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

            s = self.smtp_connect(smtp_address, smtp_username, smtp_password,
                                  smtp_port=smtp_port, use_ssl=use_ssl)

            if not s:
                return

            s.sendmail(email_from, [email_to], msg.as_string())


            if not log:
                log = email_to
            self.log('SEND', log)

            self.smtp_close(s)

        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'Error sending two-part email to %s: '+e.message % email_to)


    def process(self, mails, function):
        """
        Email processing hook, apply a processing function to any email in a list
        :param mails: List of emails
        :param function: Processing function
        """
        try:
            for mail in mails:

                if self.__service_log_enabled__ == 'DEBUG':
                    self.log('PROCESS', 'Processing function %s on mail %s' % (function.__name__, str(mail)))

                function(mail)

        except Exception as e:
            if self.__service_log_enabled__:
                self.log('ERROR', 'Processing error: %s' % e.message)

    def log(self, label, value):
        """
        Adds a new log entry
        :param service: Main service object
        :param label: Log label
        :param value: Log value
        """
        if self.__service_log__ == 'DB':
            self.add_db_log_entry(self.__service_name__, label, value)
        elif self.__service_log__ == 'CMD':
            print '%s %s %s' % (self.__service_name__, label, value)

    def data_connect(self, **kwargs):
        """
        return a new database connection object
        :param connection: DB connection string
        :return: DB connection object
        """
        SQLITE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "database/storage.sqlite")
        if not 'connection'in kwargs:
            db = DAL('sqlite://'+SQLITE_FILE, **kwargs)
        else:
            connection = kwargs['connection']
            kwargs.pop('connection', None)
            db = DAL(connection, **kwargs)
        return db

    def instance_tables(self, db):
        """
        Instance deafault loging tables in database
        :param db: DB connection object
        """
        db.define_table('log',
                        Field('source'),
                        Field('label'),
                        Field('value'),
                        Field('date', 'datetime', default=datetime.datetime.now())
                        )

        def add_db_log_entry(source, label, value):
            db.log.insert(source=source, label=label, value=value)
            db.commit()
        self.add_db_log_entry = add_db_log_entry

        def get_logs(source=None, label=None):
            if not source and not label:
                query = db.log.source
            elif source and not label:
                query = db.log.source == source
            elif not source and label:
                query = db.log.label == label
            else:
                query = (db.log.source == source) & (db.log.label == label)
            return db(query).select()
        self.get_logs = get_logs


def add(service_name):
    service_name_upper_camel_case = service_name.title().replace(' ','')
    service_name_camel_case = service_name.lower().replace(' ','_')
    service_file = os.path.join(__SERVICES_FOLDER__, service_name_camel_case)
    if not os.path.exists(service_file):
        os.makedirs(service_file)

    init_file_template = """# -*- coding: utf-8 -*-


def run():
    from %s.service import %s
    srv = %s()
    srv.run()""" % (service_name_camel_case, service_name_upper_camel_case, service_name_upper_camel_case)

    init_file_path = os.path.join(service_file, '__init__.py')
    init_file = open(init_file_path, 'w+')
    init_file.write(init_file_template)

    service_file_template = """# -*- coding: utf-8 -*-

from mailproc import MailProc

__service_name__ = '%s'
__service_version__ = '0.1'
__service_log__ = 'CMD' # change to 'DB' for production

# mail server config
mail_server = ''
mail_user = ''
mail_password = ''

class %s(MailProc):

    def __init__(self):

        # init framework parent class
        MailProc.__init__(self)

        # service info
        self.__service_name__ = __service_name__
        self.__service_version__ = __service_version__

        # enable logging
        self.set_log_type(__service_log__)
        self.enable_log()

        # instance database and default logging tables and functions
        self.db = self.data_connect()
        self.instance_tables(self.db)

    def run(self):
        mails = self.get_new_mails(mail_server, mail_user, mail_password, use_ssl=False)
        self.process(mails, self.action)

    def action(self, mail):
        # define actions for each new email
        print mail
""" % (service_name, service_name_upper_camel_case)

    service_file_path = os.path.join(service_file, 'service.py')
    service_file = open(service_file_path, 'w+')
    service_file.write(service_file_template)


def main():

    prog = 'mailproc'
    version = '%(prog)s 0.2.1'
    description = 'Mail services creation microframework.'
    epilog = version+' - (C) 2015 Carlos Cesar Caballero Díaz, a Daxlab project.'

    import argparse

    parser = argparse.ArgumentParser(prog=prog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=description,
                                     epilog=epilog)

    parser.add_argument('--version', action='version', version=version,
                        help='show program\'s version number and exit')
    parser.add_argument('-a', '--add', action='store', default=False, dest='add',
                        metavar="'Service name'",
                        help='Create a new service base template')

    args = parser.parse_args()

    start(args)


def start(args):
    if args.add:
        add(args.add)
    else:
        mailproc_proc = MailProcProcessor()
        mailproc_proc.call_services()

if __name__ == '__main__':
    main()