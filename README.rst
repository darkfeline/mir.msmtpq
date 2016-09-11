pymsmtpq
========

Script for queuing messages for sending with msmtp.

Usage
-----

::

    pymsmtpq <args>

Use just like msmtp or sendmail.  pymsmtpq will queue the message, but WON'T
SEND THEM.  You will have to send them manually::

    pymsmtpq --manage s

Send all queued messages::

    pymsmtpq --manage h

Print management help.

Configuration
-------------

Edit the constants in the source file.

Emacs configuration
-------------------

This section describes how to use pymsmtpq with Emacs to queue emails and send
asynchronously with msmtp and Emacs's sendmail support.

Configure Emacs to use pymsmtp::

    (setq message-send-mail-function 'message-send-mail-with-sendmail
          sendmail-program "~/bin/pymsmtpq")  ; Change the path as appropriate

Add a hook to flush the queue after sending::

    (add-hook 'message-sent-hook
              (lambda ()
                (start-process "pymsmtpq-flush" nil "pymsmtpq" "--manage" "s")))
