.. _deployment:

Deployment
==========

Right now mailProc is intended to run using a time-based job scheduler for
periodically executions

Cron
----

`Cron <http://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html>`_
is a time-based job scheduler in Unix-like computer operating systems.
We can use cron to periodically execute our mailProc application. In most UNIX-like
environments we can execute:

.. code-block:: sh

    crontab -e

And include the following line for execute your application every five minutes::

    */5 * * * * python /path/to/my/mailproc/app.py
