# Copyright (C) 2016 Allen Li
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

import json
import subprocess
from unittest import mock

import pytest

import mir.msmtpq.queue as queuelib


def test_queue_repr():
    queue = queuelib.Queue('/foo/bar')
    got = repr(queue)
    assert got == "Queue('/foo/bar')"


def test_queue_getitem(tmpdir):
    (tmpdir / 'sophie').write_text(
        '{"args": ["foo", "bar"], "message": "Sophie is cute"}')
    queue = queuelib.Queue(tmpdir)
    got = queue['sophie']
    assert isinstance(got, queue._message_cls)
    assert got.args == ['foo', 'bar']
    assert got.message == 'Sophie is cute'


def test_queue_getitem_missing(tmpdir):
    queue = queuelib.Queue(tmpdir)
    with pytest.raises(KeyError):
        queue['sophie']


def test_queue_setitem(tmpdir):
    (tmpdir / 'sophie').write_text(
        '{"args": ["foo", "bar"], "message": "Sophie is cute"}')
    queue = queuelib.Queue(tmpdir)
    message = queuelib.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    queue['sophie'] = message
    with (tmpdir / 'sophie').open() as file:
        got = json.load(file)
    assert got == {"args": ["foo", "bar"], "message": "Sophie is cute"}


def test_queue_delitem(tmpdir):
    (tmpdir / 'sophie').write_text('')
    queue = queuelib.Queue(tmpdir)
    del queue['sophie']
    assert not (tmpdir / 'sophie').exists()


def test_queue_add(tmpdir):
    queue = queuelib.Queue(tmpdir)
    message = queuelib.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    with mock.patch.object(
            type(message), 'key',
            new_callable=mock.PropertyMock) as key_mock:
        key_mock.return_value = 'message_key'
        got = queue.add(message)
    assert got == 'message_key'
    with (tmpdir / 'message_key').open() as file:
        got = json.load(file)
    assert got == {"args": ["foo", "bar"], "message": "Sophie is cute"}


def test_queue_len(tmpdir):
    queue = queuelib.Queue(tmpdir)
    assert len(queue) == 0
    (tmpdir / 'sophie').write_text('')
    assert len(queue) == 1


def test_queue_iter(tmpdir):
    queue = queuelib.Queue(tmpdir)
    assert list(queue) == []
    (tmpdir / 'sophie').write_text('')
    assert list(queue) == ['sophie']


def test_sendmail_repr():
    sendmail = queuelib.Sendmail('sendmail')
    got = repr(sendmail)
    assert got == "Sendmail('sendmail')"


def test_sendmail():
    message = queuelib.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    sendmail = queuelib.Sendmail('sendmail')
    with mock.patch('subprocess.run') as run:
        sendmail(message)
    assert run.called_once_with(
        ['sendmail', 'foo', 'bar'],
        input=b'Sophie is cute',
        check=True,
    )


def test_sendmail_failure():
    message = queuelib.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    sendmail = queuelib.Sendmail('sendmail')
    with mock.patch('subprocess.run') as run:
        run.side_effect = subprocess.CalledProcessError(1, 'sendmail')
        with pytest.raises(queuelib.SendmailError):
            sendmail(message)
