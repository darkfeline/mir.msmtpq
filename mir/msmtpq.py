#!/usr/bin/python3

# Copyright 2015 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
pymsmtpq
========

Script for queuing messages for sending with msmtp.

"""

import logging
import json
import os
import subprocess
import sys
import hashlib

# msmtp program path
MSMTP = 'msmtp'

# Database for storing queue
QUEUE_DIR = os.path.join(os.environ['HOME'], '.pymsmtpq.queue')

# Path to log file
LOGFILE = os.path.join(os.environ['HOME'], '.log', 'pymsmtpq.log')


class SendError(Exception):
    """Error sending message."""


def _get_message(name):
    return os.path.join(QUEUE_DIR, name)


def _send_email(prog, args, body):
    """Send an email with given program, arguments, and body.

    Raises:
        SendError: Sending failed.

    """
    process = subprocess.Popen([prog] + args, stdin=subprocess.PIPE)
    process.communicate(body.encode())
    process.wait()
    if process.returncode != 0:
        raise SendError


class Message:

    def __init__(self, args, body):
        self.args = args
        self.body = body

    def dump(self, file):
        json.dump({'args': self.args,
                   'body': self.body}, file)

    @classmethod
    def load(cls, file):
        data = json.load(file)
        return cls(data['args'], data['body'])


def queue_message(args, body):
    """Queue an msmtp message with given args and input body.

    Args:
        args: Command arguments
        body: Message body
    Returns:
        Name of queued message.

    """
    hasher = hashlib.sha1()
    hasher.update(body.encode())
    name = hasher.hexdigest()
    with open(_get_message(name), 'x') as file:
        Message(args, body).dump(file)
    logging.info('Queued %s', name)
    return name


def send_message(name):
    """Send a queued message with the given name.

    Raises:
        SendError: Sending failed.

    """
    path = _get_message(name)
    with open(path) as file:
        message = Message.load(file)
    try:
        _send_email(MSMTP, message.args, message.body)
    except SendError:
        logging.error('Could not send %s', name)
        raise
    logging.info('Sent %s', name)
    os.unlink(path)


def send_all():
    """Send all messages in queue."""
    logging.info('Sending all messages...')
    for name in os.listdir(QUEUE_DIR):
        send_message(name)
    logging.info('Sending finished.')


###############################################################################
# Command definitions

_COMMANDS = {}


def _add_command(name):
    """Make decorator to add function as command."""
    def adder(func):
        """Add function as command."""
        _COMMANDS[name] = func
        return func
    return adder


@_add_command('h')
def _cmd_print_help():
    """Print command help."""
    print("""Usage: {} --manage COMMAND

    Commands:

    h         Print this help
    s         Send all queued messages
    l         List all messages
    d <name>  Delete a message
    o <name>  Send one message

    """.format(sys.argv[0]))


@_add_command('s')
def _cmd_send_all():
    send_all()


@_add_command('l')
def _cmd_list():
    for name in os.listdir(QUEUE_DIR):
        print('Message: {}'.format(name))
        with open(_get_message(name)) as file:
            message = Message.load(file)
        print(message.args)
        print(message.body)


@_add_command('d')
def _cmd_delete(name):
    os.unlink(_get_message(name))


@_add_command('o')
def _cmd_send_one(name):
    send_message(name)


def main():
    """Entry point."""
    if not os.path.exists(os.path.dirname(LOGFILE)):
        os.mkdir(os.path.dirname(LOGFILE))
    logging.basicConfig(level='INFO', filename=LOGFILE,
                        format='%(asctime)s %(levelname)s %(message)s')

    if not os.path.exists(QUEUE_DIR):
        os.mkdir(QUEUE_DIR)

    if len(sys.argv) >= 3 and sys.argv[1] == '--manage':
        func = _COMMANDS.get(sys.argv[2], _cmd_print_help)
        func(*sys.argv[3:])
    else:
        args = sys.argv[1:]
        body = sys.stdin.read()
        queue_message(args, body)

if __name__ == '__main__':
    main()
