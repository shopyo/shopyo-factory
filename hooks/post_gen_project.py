#!/usr/bin/env python
import os
import shutil
import subprocess

PROJ_DIR = os.getcwd()


def setup_docs():

    # remove the docs folder not used
    shutil.move(
        os.path.join(
            PROJ_DIR, "doc_options", "{{ cookiecutter.doc_type }}", "docs"
        ),
        PROJ_DIR,
    )
    # move the mkdocs.yml to root if doctype is mkdocs
    if "{{ cookiecutter.doc_type }}" == "mkdocs":
        shutil.move(os.path.join(PROJ_DIR, "docs", "mkdocs.yml"), PROJ_DIR)
    # remove the doc_options folder
    shutil.rmtree(os.path.join(PROJ_DIR, "doc_options"))


def pip_compile_requirements():
    subprocess.check_call(
        ["pip-compile", os.path.join("requirements", "dev.in")]
    )
    subprocess.check_call(
        ["pip-compile", os.path.join("requirements", "tests.in")]
    )
    subprocess.check_call(
        ["pip-compile", os.path.join("requirements", "docs.in")]
    )


if __name__ == "__main__":
    setup_docs()
    # pip_compile_requirements()
