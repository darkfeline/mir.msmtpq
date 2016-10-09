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

"""Message queue classes."""

import collections.abc
import hashlib
import json
import os


class Queue(collections.abc.MutableMapping):

    """Object mapping for the queue directory."""

    def __init__(self, queue_dir):
        self.queue_dir = queue_dir

    def __getitem__(self, key):
        message_path = self._get_message_path(key)
        try:
            with open(message_path) as file:
                return Message.load(file)
        except OSError as e:
            raise KeyError(key) from e

    def __setitem__(self, key, message):
        message_path = self._get_message_path(key)
        with open(message_path, 'w') as file:
            message.dump(file)

    def __delitem__(self, key):
        message_path = self._get_message_path(key)
        os.unlink(message_path)

    def __iter__(self):
        yield from os.listdir(self.queue_dir)

    def __len__(self):
        return len(os.listdir(self.queue_dir))

    def add(self, message):
        """Queue a message and return its key."""
        self[message.key] = message
        return message.key

    def _get_message_path(self, key):
        """Get pathname for message with given key."""
        return os.path.join(self.queue_dir, key)


class Message:

    """sendmail message"""

    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self):
        return '{cls}(args={this.args!r}, body={this.body!r})'.format(
            cls=type(self).__qualname__, this=self)

    def __str__(self):
        return ('Key: {this.key}\n'
                'Args: {this.args}\n'
                '{this.body}'
                .format(this=self))

    def dump(self, file):
        """Dump message to file as JSON."""
        json.dump({'args': self.args,
                   'body': self.body}, file)

    @classmethod
    def load(cls, file):
        """Load message form JSON file."""
        data = json.load(file)
        return cls(args=data['args'],
                   body=data['body'])

    @property
    def key(self):
        """The message's key."""
        hasher = hashlib.sha1()
        hasher.update(self.body.encode())
        return hasher.hexdigest()
