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

from unittest import mock

import pytest

import mir.msmtpq.queue as queuelib


@pytest.fixture
def queue():
    """Fake Queue."""
    return dict()


@pytest.fixture
def sendmail():
    """Stub/spy Sendmail."""
    return mock.create_autospec(queuelib.Sendmail)


def test_sender_repr():
    sender = queuelib.QueueSender(
        queue=mock.sentinel.queue,
        sendmail=mock.sentinel.sendmail,
    )
    got = repr(sender)
    assert got == ("QueueSender(queue=sentinel.queue,"
                   " sendmail=sentinel.sendmail)")


def test_sender_send(queue, sendmail):
    sender = queuelib.QueueSender(queue=queue, sendmail=sendmail)
    message = queuelib.Message(
        args=['foo'],
        message='Sophie is cute.',
    )
    queue['sophie'] = message
    sender.send('sophie')
    assert len(sendmail.call_args_list) == 1
    assert sendmail.call_args == mock.call(message)
    assert 'sophie' not in queue


def test_sender_send_error(queue, sendmail):
    sendmail.side_effect = queuelib.SendmailError
    sender = queuelib.QueueSender(queue=queue, sendmail=sendmail)
    message = queuelib.Message(
        args=['foo'],
        message='Sophie is cute.',
    )
    queue['sophie'] = message
    sender.send('sophie')
    assert 'sophie' in queue


def test_sender_send_all(queue, sendmail):
    sender = queuelib.QueueSender(queue=queue, sendmail=sendmail)
    queue['sophie'] = mock.sentinel.sophie
    queue['prachta'] = mock.sentinel.prachta
    with mock.patch.object(type(sender), 'send') as send:
        sender.send_all()
    assert mock.call('sophie') in send.call_args_list
    assert mock.call('prachta') in send.call_args_list
