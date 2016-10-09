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

"""sendmail interface."""

import logging
import subprocess

logger = logging.getLogger(__name__)


class Sendmail:

    """sendmail wrapper"""

    def __init__(self, prog):
        self.prog = prog

    def __call__(self, message):
        try:
            subprocess.run([self.prog] + message.args,
                input=message.body.encode(), check=True)
        except subprocess.CalledProcessError:
            logger.error('Failed to send %s', message.key)
        else:
            logger.info('Sent %s', message.key)
