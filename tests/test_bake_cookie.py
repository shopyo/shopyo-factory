import os
import shlex
import subprocess
from contextlib import contextmanager


@contextmanager
def inside_dir(dir_path):
    """
    run code inside the given directory

    :param dir_path: path of the directory inside which to run the code
    :type dir_path: str
    """
    old_path = os.getcwd()
    try:
        os.chdir(dir_path)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(cmd, dir_path):
    """run the given command inside the specified directory

    :param cmd: the command that will be executed
    :type cmd: str
    :param dir_path: path of directory in which the command will be executed
    :type dir_path: str
    :return: return code for the command that is ran
    :rtype: int
    :raises CalledProcessError: if command exits with non zero return code
    """
    with inside_dir(dir_path):
        return subprocess.check_call(shlex.split(cmd))


def test_bake_project_with_mkdocs(cookies):
    extra_context = {
        "full_name": "Foo Bar",
        "email": "foo@bar.com",
        "github_username": "foobar",
        "project_name": "Test Project",
        "project_short_description": "my test project description",
        "doc_type": "mkdocs",
    }
    result = cookies.bake(extra_context=extra_context)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == "test_project"
    assert result.project.isdir()
    assert os.path.exists(os.path.join(result.project, "test_project", "modules"))
    assert os.path.exists(os.path.join(result.project, "test_project", "static"))
    assert os.path.exists(os.path.join(result.project, "test_project", "tests"))
    assert os.path.exists(os.path.join(result.project, "test_project", "__init__.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", ".test.prod.env"))
    assert os.path.exists(os.path.join(result.project, "test_project", "app.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "cli.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "config_demo.json"))
    assert os.path.exists(os.path.join(result.project, "test_project", "config.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "conftest.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "init.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "manage.py"))
    assert os.path.exists(os.path.join(result.project, "test_project", "wsgi.py"))
    assert os.path.exists(os.path.join(result.project, ".github", "workflows", "tests.yml"))
    assert os.path.exists(os.path.join(result.project, "docs"))
    assert os.path.exists(os.path.join(result.project, "docs", "index.md"))
    assert os.path.exists(os.path.join(result.project, "requirements"))
    assert os.path.exists(os.path.join(result.project, ".gitignore"))
    assert os.path.exists(os.path.join(result.project, "MANIFEST.in"))
    assert os.path.exists(os.path.join(result.project, "mkdocs.yml"))
    assert os.path.exists(os.path.join(result.project, "pyproject.toml"))
    assert os.path.exists(os.path.join(result.project, "README.md"))
    assert os.path.exists(os.path.join(result.project, "setup.cfg"))
    assert os.path.exists(os.path.join(result.project, "setup.py"))
    assert os.path.exists(os.path.join(result.project, "tox.ini"))


def test_run_generated_project_tests(cookies, env_bin):

    extra_context = {
        "project_name": "bar",
    }
    result = cookies.bake(extra_context=extra_context)
    env_python = os.path.join(env_bin, "python")

    assert result.exit_code == 0
    assert run_inside_dir(f"{env_python} -m pip install -r requirements/dev.txt", result.project) == 0
    assert run_inside_dir(f"{env_python} -m pip install -e .", result.project) == 0
    assert run_inside_dir(f"{env_python} -m pytest", os.path.join(result.project, "bar")) == 0

