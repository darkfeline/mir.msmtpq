# Copyright (C) 2015-2016 Allen Li
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

"""Mail queue.

This module contains classes for managing the mail queue for msmtpq.
"""

import collections.abc
import hashlib
import json
import logging
import os
import pathlib
import subprocess

logger = logging.getLogger(__name__)


class Message:

    """Represents a message to be sent with sendmail.

    Class methods:
        load -- Load message from a file

    Methods:
        dump -- Dump message to a file

    Attributes:
        args -- sendmail arguments
        message -- message (headers + body)

    Properties:
        key -- Hash key for the message
    """

    def __init__(self, args, message):
        self.args = args
        self.message = message

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.args == other.args and self.message == other.message
        else:
            return NotImplemented

    def __repr__(self):
        return '{cls}(args={this.args!r}, message={this.message!r})'.format(
            cls=type(self).__qualname__, this=self)

    def __str__(self):
        return ('Key: {this.key}\n'
                'Args: {this.args}\n'
                '{this.message}'
                .format(this=self))

    def dump(self, file):
        """Dump message to a file as JSON."""
        json.dump({'args': self.args,
                   'message': self.message}, file)

    @classmethod
    def load(cls, file):
        """Load message from a JSON file."""
        data = json.load(file)
        return cls(args=data['args'],
                   message=data['message'])

    @property
    def key(self):
        """Hash key for the message."""
        hasher = hashlib.sha1()
        hasher.update(self.message.encode())
        return hasher.hexdigest()


class Queue(collections.abc.MutableMapping):

    """Message queue backed by a file system.

    This class provides a Python Mapping interface to a message queue backed by
    a directory on a file system.  Instances can be used more or less like a
    persistent dictionary.

    Methods:
        add -- Add a message
    """

    _message_cls = Message

    def __init__(self, queue_dir):
        self._queue_dir = pathlib.Path(queue_dir)

    def __repr__(self):
        return '{cls}({queue_dir!r})'.format(
            cls=type(self).__qualname__,
            queue_dir=str(self._queue_dir))

    def __getitem__(self, key):
        try:
            with self._open_message(key) as file:
                return self._message_cls.load(file)
        except OSError as e:
            raise KeyError(key) from e

    def __setitem__(self, key, message):
        with self._open_message(key, 'w') as file:
            message.dump(file)

    def __delitem__(self, key):
        self._get_message_path(key).unlink()

    def __iter__(self):
        # XXX Python 3.6 fspath support
        yield from os.listdir(str(self._queue_dir))

    def __len__(self):
        return len(list(iter(self)))

    def add(self, message):
        """Queue a message and return its key."""
        self[message.key] = message
        return message.key

    def _get_message_path(self, key):
        """Return the Path to the message file with the given key."""
        return self._queue_dir / key

    def _open_message(self, key, mode='r'):
        """Open the message file with the given key."""
        return self._get_message_path(key).open(mode=mode)


class QueueSender:

    """Send messages in a Queue using Sendmail."""

    def __init__(self, queue, sendmail):
        self._queue = queue
        self._sendmail = sendmail

    def __repr__(self):
        return ('{cls}(queue={this._queue!r}, sendmail={this._sendmail!r})'
                .format(
                    cls=type(self).__qualname__,
                    this=self))

    def send(self, key):
        """Send message with key."""
        message = self._queue[key]
        try:
            self._sendmail(message)
        except SendmailError:
            logger.error('Failed to send %s', message.key)
        else:
            logger.info('Sent %s', message.key)
            self._queue.pop(key)

    def send_all(self):
        """Send all messages in queue."""
        logger.info('Sending all messages.')
        for key in self._queue:
            self.send(key)
        logger.info('Sending finished.')


class Sendmail:

    """Interface to sendmail program."""

    def __init__(self, prog):
        """Initialize instance.

        prog is the path to the sendmail program.
        """
        self._prog = prog

    def __repr__(self):
        return '{cls}({this._prog!r})'.format(
            cls=type(self).__qualname__,
            this=self)

    def __call__(self, message):
        """Send a Message instance with sendmail."""
        try:
            subprocess.run(
                [self._prog] + message.args,
                input=message.message.encode(), check=True)
        except subprocess.CalledProcessError as e:
            raise SendmailError(str(e)) from e


class SendmailError(Exception):
    """Error calling sendmail."""
