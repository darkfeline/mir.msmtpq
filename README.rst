mir.msmtpq
==========

.. image:: https://circleci.com/gh/project-mir/mir.msmtpq.svg?style=shield
   :target: https://circleci.com/gh/project-mir/mir.msmtpq
   :alt: CircleCI
.. image:: https://codecov.io/gh/project-mir/mir.msmtpq/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/project-mir/mir.msmtpq
   :alt: Codecov
.. image:: https://badge.fury.io/py/mir.msmtpq.svg
   :target: https://badge.fury.io/py/mir.msmtpq
   :alt: PyPi Release

mir.msmtpq is a message queue for msmtp.

Usage
-----

msmtpq is a drop-in replacement for sendmail or msmtp.  Unlike
sendmail or msmtp however, msmtpq will only queue messages.  This
allows you to control when messages are sent.  Currently, msmtpq uses
``msmtp`` in the search path for sending messages.

Queued messages can be sent using::

  msmtpq --manage send

Queued messages can be listed using::

  msmtpq --manage list

Queued messages are stored in ``~/.config/msmtpq/queue``.  Logs are
stored in ``~/.logs``.
