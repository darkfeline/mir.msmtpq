# Copyright 2015-2016 Allen Li
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

import argparse
import logging
import os
import sys

import mir.msmtpq.queue as queue_mod
import mir.msmtpq.sendmail as sendmail_mod

MSMTP_PATH = 'msmtp'
QUEUE_DIR = os.path.join(os.environ['HOME'], '.msmtpq.queue')
LOGDIR = os.path.join(os.environ['HOME'], '.log')
LOGFILE_NAME = 'msmtpq.log'
LOGFILE_PATH = os.path.join(LOGDIR, LOGFILE_NAME)

logger = logging.getLogger(__name__)


class Sender:

    def __init__(self, queue, sendmail):
        self.queue = queue
        self.sendmail = sendmail

    def send(self, key):
        """Send message with key."""
        message = self.queue[key]
        self.sendmail(message)
        self.queue.pop(key)

    def send_all(self):
        """Send all messages in queue."""
        logger.info('Sending all messages.')
        for key in self.queue:
            self.send(key)
        logging.info('Sending finished.')


def _get_queue():
    return queue_mod.Queue(QUEUE_DIR)


def _get_sendmail():
    return sendmail_mod.Sendmail(MSMTP_PATH)


def _get_sender():
    return Sender(queue=_get_queue(), sendmail=_get_sendmail())


###############################################################################
# Command definitions

_COMMANDS = {}


def _add_command(name):
    """Decorator to add command."""
    def decorate(func):
        _COMMANDS[name] = func
        return func
    return decorate


@_add_command('send')
def _send_all():
    sender = _get_sender()
    sender.send_all()


@_add_command('list')
def _list():
    queue = _get_queue()
    for key in queue:
        message = queue[key]
        print(message)


def _setup_logging():
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
    logging.basicConfig(level='INFO', filename=LOGFILE_PATH,
                        format='%(asctime)s %(levelname)s %(message)s')


def main():
    _setup_logging()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true', help='Print help.')
    parser.add_argument('--manage', nargs=1, choices=_COMMANDS.keys(),
                        help='Queue management.')
    args, extra_args = parser.parse_known_args()

    if args.help:
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(QUEUE_DIR):
        os.mkdir(QUEUE_DIR)

    if args.manage:
        func = _COMMANDS[args.manage[0]]
        func(*extra_args)
    else:
        body = sys.stdin.read()
        queue = _get_queue()
        queue.add(queue_mod.Message(
            args=extra_args,
            body=body))

if __name__ == '__main__':
    main()
