.. _api:

API
===

.. module:: mailproc

This part of the documentation covers all the interfaces of mailProc.
For parts where mailProc depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

Application Object
------------------

.. autoclass:: mailproc.Mailproc
    :members:
    :inherited-members:

Email Object
------------

.. autoclass:: mailproc.Email
    :members:

.. module:: mailproc.transports

Receiver Transports
-------------------

.. autoclass:: mailproc.transports.BaseReceiverTransport
    :members:
    :inherited-members:

.. autoclass:: mailproc.transports.FileReceiverTransport
    :members:
    :inherited-members:

.. autoclass:: mailproc.transports.ImapReceiverTransport
    :members:
    :inherited-members:

.. autoclass:: mailproc.transports.ImapIdleReceiverTransport
    :members:
    :inherited-members:

Sender Transports
-----------------

.. autoclass:: mailproc.transports.BaseSenderTransport
    :members:
    :inherited-members:

.. autoclass:: mailproc.transports.FileSenderTransport
    :members:
    :inherited-members:

.. autoclass:: mailproc.transports.SmtpSenderTransport
    :members:
    :inherited-members:

