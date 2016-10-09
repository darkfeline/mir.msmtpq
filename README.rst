mir.msmtpq
==========

Script for queuing messages for sending with msmtp.

Usage
-----

::

    msmtpq <args>

Use just like msmtp or sendmail.  pymsmtpq will queue the email, but WON'T
SEND THEM.  You will have to send them manually::

    msmtpq --manage send

This allows you to control when emails are sent, allowing you to queue up emails
when you don't have Internet access.

Emacs configuration
-------------------

This section describes how to use pymsmtpq with Emacs to queue emails and send
asynchronously with msmtp and Emacs's sendmail support.

Configure Emacs to use pymsmtp::

    (setq message-send-mail-function 'message-send-mail-with-sendmail
          sendmail-program "~/bin/msmtpq")  ; Change the path as appropriate

Add a hook to flush the queue after sending::

    (add-hook 'message-sent-hook
              (lambda ()
                (start-process "msmtpq-flush" nil "msmtpq" "--manage" "s")))
