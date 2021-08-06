import importlib
import os
import sys
from subprocess import run

import click

from shopyo.api.file import tryrmcache
from shopyo.api.file import tryrmfile
from shopyo.api.file import tryrmtree
from shopyo.api.constants import SEP_CHAR
from shopyo.api.constants import SEP_NUM

def _clean(verbose=False):
    """
    Deletes shopyo.db and migrations/ if present in current working directory.
    Deletes all __pycache__ folders starting from current working directory
    all the way to leaf directory.

    Parameters
    ----------
        - verbose: flag to indicate whether to print to result of clean to
            stdout or not.
        - db: db to be cleaned

    Returns
    -------
    None
        ...

    """
    from {{ cookiecutter.project_slug }}.init import db

    click.echo("Cleaning...")
    click.echo(SEP_CHAR * SEP_NUM)

    db.drop_all()
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")

    if verbose:
        click.echo("[x] all tables dropped")

    tryrmcache(os.getcwd(), verbose=verbose)
    tryrmfile(os.path.join(os.getcwd(), "shopyo.db"), verbose=verbose)
    tryrmtree(os.path.join(os.getcwd(), "migrations"), verbose=verbose)

    click.echo("")


def _upload_data(verbose=False):
    click.echo("Uploading initial data to db...")
    click.echo(SEP_CHAR * SEP_NUM)

    root_path = os.getcwd()

    for folder in os.listdir(os.path.join(root_path, "modules")):
        if folder.startswith("__"):  # ignore __pycache__
            continue
        if folder.startswith("box__"):
            # boxes
            for sub_folder in os.listdir(os.path.join(root_path, "modules", folder)):
                if sub_folder.startswith("__"):  # ignore __pycache__
                    continue
                elif sub_folder.endswith(".json"):  # box_info.json
                    continue

                try:
                    upload = importlib.import_module(
                        f"{{ cookiecutter.project_slug }}.modules.{folder}.{sub_folder}.upload"
                    )
                    upload.upload(verbose=verbose)
                except ImportError as e:
                    if verbose:
                        click.echo(f"[ ] {e}")
        else:
            # apps
            try:
                upload = importlib.import_module(f"{{ cookiecutter.project_slug }}.modules.{folder}.upload")
                upload.upload(verbose=verbose)
            except ImportError as e:
                if verbose:
                    click.echo(f"[ ] {e}")

    click.echo("")


def _run_app(mode):
    """helper command for running shopyo flask app in debug/production mode"""
    app_path = os.path.join(os.getcwd(), "app.py")

    if not os.path.exists(app_path):
        click.secho(f"Unable to find `app.py` in {os.getcwd()}", fg="red")
        sys.exit(1)

    os.environ["FLASK_APP"] = f"app:create_app('{mode}')"
    os.environ["FLASK_ENV"] = mode
    run(["flask", "run"])
