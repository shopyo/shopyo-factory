import os
import shutil

import pytest
from {{ cookiecutter.project_slug }}.app import app as _app
from {{ cookiecutter.project_slug }}.app import create_app

from shopyo.api.file import tryrmtree


@pytest.fixture
def app(tmpdir, app_type):
    src = os.path.join(_app.instance_path, "config.py")
    dest = tmpdir.join("temp_config.py")
    dest.write("")
    shutil.copy(src, dest)
    tryrmtree(_app.instance_path)
    dev_app = create_app(app_type)
    yield dev_app
    shutil.copy(dest, src)


@pytest.fixture
def restore_cwd():
    old = os.getcwd()
    yield
    os.chdir(old)
