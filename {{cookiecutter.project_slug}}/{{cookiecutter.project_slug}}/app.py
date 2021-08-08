import importlib
import os
import sys

import jinja2
from flask import Flask
from flask import send_from_directory
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_login import current_user

from shopyo.api.file import trycopy
from {{ cookiecutter.project_slug }}.config import app_config
from {{ cookiecutter.project_slug }}.init import csrf
from {{ cookiecutter.project_slug }}.init import db
from {{ cookiecutter.project_slug }}.init import login_manager
from {{ cookiecutter.project_slug }}.init import ma
from {{ cookiecutter.project_slug }}.init import mail
from {{ cookiecutter.project_slug }}.init import migrate
from {{ cookiecutter.project_slug }}.init import modules_path
from {{ cookiecutter.project_slug }}.modules.box__default.settings.helpers import get_setting
from {{ cookiecutter.project_slug }}.modules.box__default.settings.models import Settings
from {{ cookiecutter.project_slug }}.{{ cookiecutter.project_slug }}_admin import DefaultModelView
from {{ cookiecutter.project_slug }}.{{ cookiecutter.project_slug }}_admin import MyAdminIndexView


base_path = os.path.dirname(os.path.abspath(__file__))


def create_app(config_name="development"):

    global_entities = {}
    app = Flask(__name__, instance_relative_config=True)
    load_config_from_obj(app, config_name)
    load_config_from_instance(app, config_name)
    create_config_json()
    load_extensions(app)
    setup_flask_admin(app)
    register_devstatic(app)
    load_blueprints(app, global_entities)
    setup_theme_paths(app)
    inject_global_vars(app, global_entities)
    return app


def load_config_from_obj(app, config_name):

    try:
        configuration = app_config[config_name]
    except KeyError as e:
        print(
            f"[ ] Invalid config name {e}. Available configurations are: "
            f"{list(app_config.keys())}\n"
        )
        sys.exit(1)

    app.config.from_object(configuration)


def load_config_from_instance(app, config_name):

    if config_name != "testing":
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)

    # create empty instance folder and empty config if not present
    try:
        os.makedirs(app.instance_path)
        with open(os.path.join(app.instance_path, "config.py"), "a"):
            pass
    except OSError:
        pass


def create_config_json():
    if not os.path.exists("config.json"):
        trycopy("config_demo.json", "config.json")


def load_extensions(app):
    migrate.init_app(app, db)
    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def setup_flask_admin(app):
    admin = Admin(
        app,
        name="My App",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView(),
    )
    admin.add_view(DefaultModelView(Settings, db.session))
    admin.add_link(MenuLink(name="Logout", category="", url="/auth/logout?next=/admin"))


def register_devstatic(app):
    @app.route("/devstatic/<path:boxormodule>/f/<path:filename>")
    def devstatic(boxormodule, filename):
        if app.config["DEBUG"]:
            module_static = os.path.join(modules_path, boxormodule, "static")
            return send_from_directory(module_static, filename=filename)


def load_blueprints(app, global_entities):

    for folder in os.listdir(os.path.join(base_path, "modules")):
        if folder.startswith("__"):  # ignore __pycache__
            continue

        if folder.startswith("box__"):
            # boxes
            for sub_folder in os.listdir(os.path.join(base_path, "modules", folder)):
                if sub_folder.startswith("__"):  # ignore __pycache__
                    continue
                elif sub_folder.endswith(".json"):  # box_info.json
                    continue
                try:
                    sys_mod = importlib.import_module(
                        f"{{ cookiecutter.project_slug }}.modules.{folder}.{sub_folder}.view"
                    )
                    app.register_blueprint(getattr(sys_mod, f"{sub_folder}_blueprint"))
                except AttributeError:
                    pass
                try:
                    mod_global = importlib.import_module(
                        f"{{ cookiecutter.project_slug }}.modules.{folder}.{sub_folder}.global"
                    )
                    global_entities.update(mod_global.available_everywhere)
                except ImportError:
                    pass

        else:
            # apps
            try:
                mod = importlib.import_module(f"{{ cookiecutter.project_slug }}.modules.{folder}.view")
                app.register_blueprint(getattr(mod, f"{folder}_blueprint"))
            except AttributeError:
                # print("[ ] Blueprint skipped:", e)
                pass
            try:
                mod_global = importlib.import_module(f"{{ cookiecutter.project_slug }}.modules.{folder}.global")
                global_entities.update(mod_global.available_everywhere)
            except ImportError:
                # print(f"[ ] {e}")
                pass


def setup_theme_paths(app):
    with app.app_context():
        front_theme_dir = os.path.join(
            app.config["BASE_DIR"], "static", "themes", "front"
        )
        back_theme_dir = os.path.join(
            app.config["BASE_DIR"], "static", "themes", "back"
        )
        my_loader = jinja2.ChoiceLoader(
            [
                app.jinja_loader,
                jinja2.FileSystemLoader([front_theme_dir, back_theme_dir]),
            ]
        )
        app.jinja_loader = my_loader


def inject_global_vars(app, global_entities):
    @app.context_processor
    def inject_global_vars():
        APP_NAME = get_setting("APP_NAME")

        base_context = {
            "APP_NAME": APP_NAME,
            "len": len,
            "current_user": current_user,
        }
        base_context.update(global_entities)

        return base_context
