import pytest
import subprocess
import sys
import os


@pytest.fixture(scope="session")
def env_bin(self, tmp_path):

    old = os.getcwd()
    os.chdir(tmp_path)
    # create a new virtual environment(venv)
    subprocess.check_call([sys.executable, "-m", "venv", "env"])
    # store path for python and shopyo executable of venv for the case when OS
    #  is Unix
    env_bin = os.path.join(os.getcwd(), "env", "bin")
    # if OS is Windows, update the python and shopyo executable
    if sys.platform == "win32":
        env_bin = os.path.join(os.getcwd(), "env", "Scripts")
        # shopyo_env = os.path.join(os.getcwd(), "env", "Scripts", "shopyo")
    # update pip of venv
    env_python = os.path.join(env_bin, "python")
    subprocess.check_call([env_python, "-m", "pip", "install", "--upgrade", "pip"])
    # install the shopyo package from dist added earlier
    # subprocess.check_call(
    #     [python_env, "-m", "pip", "install", "-e", "."]
    # )
    # run shopyo help command followed by new command
    print("\ninstalling env...")
    # subprocess.check_call(["shopyo", "--help"])
    os.chdir(old)
    return env_bin

def shopyo_env(env_bin):

    env_python = os.path.join(env_bin, "python")
    subprocess.check_call(
        [env_python, "-m", "pip", "install", "-e", "."]
    )
