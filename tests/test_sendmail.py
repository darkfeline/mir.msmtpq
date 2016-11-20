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

import subprocess
from unittest import mock

import pytest

from mir import msmtpq


def test_sendmail():
    message = msmtpq.queue.Message(
        args=['foo', 'bar'],
        body='Sophie is cute',
    )
    sendmail = msmtpq.sendmail.Sendmail('sendmail')
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
        body='Sophie is cute',
    )
    sendmail = msmtpq.sendmail.Sendmail('sendmail')
    with mock.patch('subprocess.run') as run:
        run.side_effect = subprocess.CalledProcessError(1, 'sendmail')
        with pytest.raises(subprocess.CalledProcessError):
            sendmail(message)
