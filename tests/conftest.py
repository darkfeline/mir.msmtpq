import pathlib

import pytest


@pytest.fixture
def tmpdir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp('tmpdir')
    return pathlib.Path(str(tmpdir))
