"""
file: cli.py
description: Add your custom cli commands here
documentation: https://click.palletsprojects.com/en/7.x/

You will need to run ``python -m pip install -e .`` to load the setup.py
which contains the entry point to this file before being able to run your
custom commands

Usage ``{{ cookiecutter.project_slug }} [OPTIONS] COMMAND [ARGS]...``

"""

# from {{ cookiecutter.project_slug }} import __version__
# import click

import os
import sys
import importlib
from subprocess import PIPE
from subprocess import run

import click
from flask.cli import FlaskGroup
from flask.cli import pass_script_info

from {{ cookiecutter.project_slug }}.cli_helper import _clean
from {{ cookiecutter.project_slug }}.cli_helper import _upload_data
from {{ cookiecutter.project_slug }}.database import autoload_models
from shopyo.api.cmd_helper import _collectstatic
from shopyo.api.constants import SEP_CHAR
from shopyo.api.constants import SEP_NUM
from shopyo.api.info import printinfo


def _create_shopyo_app(info):
    sys.path.insert(0, os.getcwd())

    try:
        from {{ cookiecutter.project_slug }}.app import create_app
    except Exception as e:
        print(e)
        return None

    config_name = info.data.get("config") or "development"

    return create_app(config_name=config_name)


@click.group(cls=FlaskGroup, create_app=_create_shopyo_app)
@click.option("--config", default="development", help="Flask app configuration type")
@pass_script_info
def cli(info, **parmams):
    """CLI for shopyo"""
    printinfo()
    config_name = parmams["config"]
    info.data["config"] = config_name
    os.environ["FLASK_APP"] = f"app:create_app('{config_name}')"
    os.environ["FLASK_ENV"] = config_name



@cli.command("clean")
@click.option("--verbose", "-v", is_flag=True, default=False)
def clean(verbose):
    """removes ``__pycache__``, ``migrations/``, ``shopyo.db`` files and drops
    ``db`` if present
    """
    _clean(verbose=verbose)


@cli.command("initialise")
@click.option("--verbose", "-v", is_flag=True, default=False)
def initialise(verbose):
    """
    Creates ``db``, ``migration/``, adds default users, add settings
    """
    click.echo("initializing...")

    # drop db, remove mirgration/ and shopyo.db
    _clean(verbose=verbose)

    # load all models available inside modules
    autoload_models(verbose=verbose)

    # add a migrations folder to your application.
    click.echo("Creating db...")
    click.echo(SEP_CHAR * SEP_NUM)
    if verbose:
        run(["flask", "db", "init"])
    else:
        run(["flask", "db", "init"], stdout=PIPE, stderr=PIPE)
    click.echo("")

    # generate an initial migration i.e autodetect changes in the
    # tables (table autodetection is limited. See
    # https://flask-migrate.readthedocs.io/en/latest/ for more details)
    click.echo("Migrating db...")
    click.echo(SEP_CHAR * SEP_NUM)
    if verbose:
        run(["flask", "db", "migrate"])
    else:
        run(["flask", "db", "migrate"], stdout=PIPE, stderr=PIPE)
    click.echo("")

    click.echo("Upgrading db...")
    click.echo(SEP_CHAR * SEP_NUM)
    if verbose:
        run(["flask", "db", "upgrade"])
    else:
        run(["flask", "db", "upgrade"], stdout=PIPE, stderr=PIPE)
    click.echo("")

    # collect all static folders inside modules/ and add it to global
    # static/
    _collectstatic(verbose=verbose)

    # Upload models data in upload.py files inside each module
    _upload_data(verbose=verbose)

    click.echo("All Done!")


if __name__ == "__main__":
    cli()
