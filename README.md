pymsmtpq
========

Script for queuing messages for sending with msmtp.

Usage
-----

    pymsmtpq <args>

Use just like msmtp or sendmail.  pymsmtpq will queue the message and then
attempt to send all queued messages in a forked process.

    pymsmtp --manage s

Send all queued messages.

    pymsmtp --manage h

Print management help.

Configuration
-------------

Edit the constants in the source file.
