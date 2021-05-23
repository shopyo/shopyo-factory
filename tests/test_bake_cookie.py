import os


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

    print(result.project)

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
