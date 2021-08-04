import pytest
import subprocess
import sys
import os


@pytest.fixture
def env_bin(tmp_path):
    
    # create a new virtual environment(venv)
    subprocess.check_call([sys.executable, "-m", "venv", tmp_path / "env"])
    
    # store path for python executable of venv
    env_bin = os.path.join(tmp_path, "env", "bin")
    
    # if OS is Windows, update the python path
    if sys.platform == "win32":
        env_bin = os.path.join(tmp_path, "env", "Scripts")

    env_python = os.path.join(env_bin, "python")
    
    # update pip of venv
    subprocess.check_call([env_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
    
    return env_bin
