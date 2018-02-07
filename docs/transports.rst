.. _quickstart:

Transports
==========

mailProc transports are aimed to provide interaction with email servers.


Receiver Transports
-------------------

Receiver transports are used to obtain emails from the server. They exposes
a :func:`~mailproc.transports.BaseReceiverTransport.connect` method which will
start a connection with the server, a :func:`~mailproc.transports.BaseReceiverTransport.get_mails`
method which will obtain emails from the server and a :func:`~mailproc.transports.BaseReceiverTransport.close`
method which will close the connection with the server.


File Receiver Transport
~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~mailproc.transports.FileReceiverTransport` class looks for raw emails
in a directory. Among other transports, the :func:`~mailproc.transports.FileReceiverTransport.connect`
and :func:`~mailproc.transports.FileReceiverTransport.close` methods don't need to be called.

Example::

    from mailproc.transports import FileReceiverTransport

    receiver_transport = FileReceiverTransport("/emails/directory")
    mails = receiver_transport.get_mails()

Imap Receiver Transport
~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~mailproc.transports.ImapReceiverTransport` class looks for emails
in an IMAP server

Example::

    from mailproc.transports import ImapReceiverTransport

    receiver_transport = ImapReceiverTransport(
        "imap.server.com",
        "imap_username",
        "imap_password"
    )

    receiver_transport.connect()

    mails = receiver_transport.get_mails()

    receiver_transport.close()


Imap Idle Receiver Transport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Experimental

The :class:`~mailproc.transports.ImapIdleReceiverTransport` class aims to establish
an IDLE connection to an IMAP server for a fast and efficient email retrieving.
The :func:`~mailproc.transports.BaseReceiverTransport.get_mails` method will require
a callback function to be passed as argument for running actions on every new
obtained email.

Example::

    from mailproc import Mailproc
    from mailproc.transports import ImapIdleReceiverTransport

    app = Mailproc("my_app_name")

    receiver_transport = ImapIdleReceiverTransport(
        "imap.server.com",
        "imap_username",
        "imap_password"
    )

    receiver_transport.connect()

    receiver_transport.get_mails(app.run)

    receiver_transport.close()


Sender Transports
-----------------

Sender transports are used to send emails. They exposes
a :func:`~mailproc.transports.BaseSenderTransport.connect` method which will
start a connection with the server, a :func:`~mailproc.transports.BaseSenderTransport.send_mail`
method which will send a new email and a :func:`~mailproc.transports.BaseSenderTransport.close`
method which will close the connection with the server.


File Sender Transport
~~~~~~~~~~~~~~~~~~~~~

The :class:`~mailproc.transports.FileSenderTransport` class creates raw emails
in a directory. Unlike other transports, the :func:`~mailproc.transports.FileSenderTransport.connect`
and :func:`~mailproc.transports.FileSenderTransport.close` methods don't need to be called.

Example::

    from mailproc.transports import FileSenderTransport

    sender_transport = FileSenderTransport("/emails/directory")

    sender_transport.send_mail(
        "fromaddres@example.com",
        "toaddres@example.com",
        "subject",
        "body"
    )


SMTP Sender Transport
~~~~~~~~~~~~~~~~~~~~~

The :class:`~mailproc.transports.SmtpSenderTransport` class sends emails using the SMTP
protocol.

Example::

    from mailproc.transports import SmtpSenderTransport

    sender_transport = SmtpSenderTransport(
        "smtp.server.com",
        "smtp_username",
        "smtp_password"
    )

    sender_transport.connect()

    sender_transport.send_mail(
        "fromaddres@example.com",
        "toaddres@example.com",
        "subject",
        "body"
    )

    sender_transport.close()

