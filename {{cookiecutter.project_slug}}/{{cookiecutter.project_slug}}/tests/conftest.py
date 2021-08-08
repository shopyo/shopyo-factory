import os
import shutil

import pytest

from shopyo.api.file import tryrmtree
from {{ cookiecutter.project_slug }}.app import create_app


@pytest.fixture(scope="module")
def temp_app():
    return create_app("testing")


@pytest.fixture
def app(tmpdir, app_type, temp_app):
    src = os.path.join(temp_app.instance_path, "config.py")
    dest = tmpdir.join("temp_config.py")
    dest.write("")
    shutil.copy(src, dest)
    tryrmtree(temp_app.instance_path)
    dev_app = create_app(app_type)
    yield dev_app
    shutil.copy(dest, src)


@pytest.fixture
def restore_cwd():
    old = os.getcwd()
    yield
    os.chdir(old)
