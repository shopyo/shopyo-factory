import pytest
import subprocess
import sys
import os


@pytest.fixture(scope="session")
def env_bin():
    # create a new virtual environment(venv)
    subprocess.check_call([sys.executable, "-m", "venv", "env"])
    # store path for python executable of venv
    env_bin = os.path.join(os.getcwd(), "env", "bin")
    # if OS is Windows, update the python path
    if sys.platform == "win32":
        env_bin = os.path.join(os.getcwd(), "env", "Scripts")

    env_python = os.path.join(env_bin, "python")
    # update pip of venv
    subprocess.check_call([env_python, "-m", "pip", "install", "--upgrade", "pip"])
    return env_bin
