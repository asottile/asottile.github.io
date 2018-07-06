#!/usr/bin/env python
"""This script will bootstrap a virtualenv from only a python interpreter."""
from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib
import hashlib
import io
import os.path
import shutil
import subprocess
import sys
import tarfile


if str is bytes:
    from urllib import urlopen
else:
    from urllib.request import urlopen


TGZ = 'https://files.pythonhosted.org/packages/33/bc/fa0b5347139cd9564f0d44ebd2b147ac97c36b2403943dbee8a25fd74012/virtualenv-16.0.0.tar.gz'  # noqa
EXPECTED_SHA256 = 'ca07b4c0b54e14a91af9f34d0919790b016923d157afda5efdde55c96718f752'  # noqa
PKG_PATH = '.virtualenv-pkg'


def clean():
    if os.path.exists(PKG_PATH):
        shutil.rmtree(PKG_PATH)


@contextlib.contextmanager
def clean_path():
    try:
        yield
    finally:
        clean()


def main(argv=None):
    clean()

    print('Downloading ' + TGZ)
    tar_contents = io.BytesIO(urlopen(TGZ).read())
    actual_sha256 = hashlib.sha256(tar_contents.getvalue()).hexdigest()
    if actual_sha256 != EXPECTED_SHA256:
        raise AssertionError(actual_sha256, EXPECTED_SHA256)
    with contextlib.closing(tarfile.open(fileobj=tar_contents)) as tarfile_obj:
        # Chop off the first path segment to avoid having the version in
        # the path
        for member in tarfile_obj.getmembers():
            _, _, member.name = member.name.partition('/')
            if member.name:
                tarfile_obj.extract(member, PKG_PATH)
    print('Done.')

    with clean_path():
        return subprocess.call(
            (sys.executable, os.path.join(PKG_PATH, 'virtualenv.py')) +
            tuple(sys.argv[1:])
        )


if __name__ == '__main__':
    exit(main())
