.. _quickstart:

Quickstart
==========

Eager to get started?  This page gives a good introduction to mailProc.  It
assumes you already have mailProc installed.  If you do not, head over to the
:ref:`installation` section.


A Minimal Application
---------------------

A minimal malproc application looks something like this::

    from mailproc import Mailproc
    from mailproc.transports import ImapReceiverTransport

    app = Mailproc("my_app_name")

    @app.route_from('test@test.com')
    def hello_world(mail):
        print("hello", mail)

    receiver_transport = ImapReceiverTransport('mail.mydomain.com', 'username', 'password')
    receiver_transport.connect()
    mails = receiver_transport.get_mails()
    receiver_transport.close()

    app.run(mails)

So what did that code do?

1. First we imported the :class:`~mailproc.Mailproc` class. An instance of this
   class will be our running application.
2. Next we import the :class:`~mailproc.transports.ImapReceiverTransport` class
   An instance of this class will obtain emails from a mail box.
3. Next we create an instance of :class:`~mailproc.Mailproc` class. The first
   argument is the name of the current application.
4. We then use the :meth:`~mailproc.Mailproc.route_from` decorator to tell mailproc
   what email 'From' address  will trigger our function.
5. The function get's a mail parameter with the email.Message object triggering him.
6. Next we create an instance of :class:`~mailproc.transports.ImapReceiverTransport`
   class. And we set the server, user name and password parameters
7. Next we start the transport connection.
8. We obtain unread emails from account
9. And we close the transport connection.
10. Next we call for the the :class:`~mailproc.Mailproc` instance to run the
    registered triggers for the obtained emails

Just save it as :file:`hello.py` or something similar. Make sure to not call
your application :file:`mailproc.py` because this would conflict with mailProc
itself.

To run the application you can call it::

    $ python hello.py

This launches a single run for the application, which is good enough for testing
but probably not what you want to use in production. For deployment options see
:ref:`deployment`.

Routing
-------

mailProc routes mails to functions similar as modern web applications frameworks
do. We can use the default :meth:`~mailproc.Mailproc.route_from` and
:meth:`~mailproc.Mailproc.route_subject` decorators to trigger actions based on
email 'From' address and subject.

Use the :meth:`~mailproc.Mailproc.route_from` decorator to bind a function to a URL. ::

    @app.route_from('*.@example.com')
    def trigger_example(mail):
        """
        Run function for all received emails of example.com domain
        """
        print(mail)

    @app.route_from('<username>@example.com')
    def trigger_example(username, mail):
        """
        Run function for all received emails of example.com domain and get username as parameter
        """
        print(username, mail)

The :meth:`~mailproc.Mailproc.route_subject` decorator can be used in a similar
way for triggering actions based on the email subject.

Logging
-------

Sometimes you might be in a situation where you deal with data that
should be correct, but actually is not. This might be caused by a user
tampering with the data, or the client code failing.

In this situations you may want to log that something fishy happened.
This is where loggers come in handy. We can use the default python logger.

Here are some example log calls::

    import logging
    logging.debug('A value for debugging')
    logging.warning('A warning occurred (%d apples)', 42)
    logging.error('An error occurred')

You can read the official `logging
documentation <https://docs.python.org/library/logging.html>`_ for more
information.