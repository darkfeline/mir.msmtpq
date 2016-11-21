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

import io
import json
import subprocess
from unittest import mock

import pytest

from mir import msmtpq


def test_message_eq():
    message1 = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    message2 = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert message1 == message2


def test_message_eq_different_args():
    message1 = msmtpq.queue.Message(
        args=['foo'],
        message='Sophie is cute',
    )
    message2 = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert message1 != message2


def test_message_eq_different_message():
    message1 = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is a dork',
    )
    message2 = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert message1 != message2


def test_message_eq_different_type():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert message != 0


def test_message_repr():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert repr(message) == \
        "Message(args=['foo', 'bar'], message='Sophie is cute')"


def test_message_str():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )

    with mock.patch.object(
            type(message), 'key',
            new_callable=mock.PropertyMock) as key_mock:
        key_mock.return_value = 'message_key'
        got = str(message)
    assert got == """\
Key: message_key
Args: ['foo', 'bar']
Sophie is cute"""


def test_message_key():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    assert message.key == '7e63d917011ecb90b52e02ff5ea0b9da9daeb7c4'


def test_message_dump():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    file = io.StringIO()
    message.dump(file)
    file.seek(0)
    got = json.load(file)
    assert got == {'args': ['foo', 'bar'],
                   'message': 'Sophie is cute'}


def test_message_load():
    file = io.StringIO('{"args": ["foo", "bar"], "message": "Sophie is cute"}')
    message = msmtpq.queue.Message.load(file)
    assert message.args == ['foo', 'bar']
    assert message.message == 'Sophie is cute'


def test_queue_getitem(tmpdir):
    (tmpdir / 'sophie').write_text(
        '{"args": ["foo", "bar"], "message": "Sophie is cute"}')
    queue = msmtpq.queue.Queue(tmpdir)
    got = queue['sophie']
    assert isinstance(got, queue._message_cls)
    assert got.args == ['foo', 'bar']
    assert got.message == 'Sophie is cute'


def test_queue_getitem_missing(tmpdir):
    queue = msmtpq.queue.Queue(tmpdir)
    with pytest.raises(KeyError):
        queue['sophie']


def test_queue_setitem(tmpdir):
    (tmpdir / 'sophie').write_text(
        '{"args": ["foo", "bar"], "message": "Sophie is cute"}')
    queue = msmtpq.queue.Queue(tmpdir)
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    queue['sophie'] = message
    with (tmpdir / 'sophie').open() as file:
        got = json.load(file)
    assert got == {"args": ["foo", "bar"], "message": "Sophie is cute"}


def test_queue_delitem(tmpdir):
    (tmpdir / 'sophie').write_text('')
    queue = msmtpq.queue.Queue(tmpdir)
    del queue['sophie']
    assert not (tmpdir / 'sophie').exists()


def test_queue_add(tmpdir):
    queue = msmtpq.queue.Queue(tmpdir)
    message = msmtpq.queue.Message(
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
    queue = msmtpq.queue.Queue(tmpdir)
    assert len(queue) == 0
    (tmpdir / 'sophie').write_text('')
    assert len(queue) == 1


def test_queue_iter(tmpdir):
    queue = msmtpq.queue.Queue(tmpdir)
    assert list(queue) == []
    (tmpdir / 'sophie').write_text('')
    assert list(queue) == ['sophie']


def test_sendmail():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    sendmail = msmtpq.queue.Sendmail('sendmail')
    with mock.patch('subprocess.run') as run:
        sendmail(message)
    assert run.called_once_with(
        ['sendmail', 'foo', 'bar'],
        input=b'Sophie is cute',
        check=True,
    )


def test_sendmail_failure():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        message='Sophie is cute',
    )
    sendmail = msmtpq.queue.Sendmail('sendmail')
    with mock.patch('subprocess.run') as run:
        run.side_effect = subprocess.CalledProcessError(1, 'sendmail')
        with pytest.raises(subprocess.CalledProcessError):
            sendmail(message)
