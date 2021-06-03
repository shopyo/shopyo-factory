import importlib
import json
import os
import sys

import jinja2
from flask import Flask
from flask import redirect
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin import expose
from flask_admin.contrib import sqla as flask_admin_sqla
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from shopyo.api.file import trycopy

#
# Flask admin setup
#


class DefaultModelView(flask_admin_sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("auth.login", next=request.url))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("auth.login", next=request.url))

    @expose("/")
    def index(self):
        if not current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for("auth.login"))
        return super().index()

    @expose("/dashboard")
    def indexs(self):
        if not current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for("auth.login"))
        return super().index()

#
# secrets files
#

try:
    if not os.path.exists("config.json"):
        trycopy("config_demo.json", "config.json")
except PermissionError as e:
    print(
        "Cannot continue, permission error"
        "initializing config.py and config.json, "
        "copy and rename them yourself!"
    )
    raise e


base_path = os.path.dirname(os.path.abspath(__file__))


def create_app(config_name="development"):

    from {{ cookiecutter.project_slug }}.config import app_config
    from {{ cookiecutter.project_slug }}.init import db
    from {{ cookiecutter.project_slug }}.init import login_manager
    from {{ cookiecutter.project_slug }}.init import ma
    from {{ cookiecutter.project_slug }}.init import mail
    from {{ cookiecutter.project_slug }}.init import migrate
    from {{ cookiecutter.project_slug }}.init import modules_path
    from {{ cookiecutter.project_slug }}.modules.box__default.settings.helpers import get_setting
    from {{ cookiecutter.project_slug }}.modules.box__default.settings.models import Settings

    app = Flask(__name__, instance_relative_config=True)

    try:
        configuration = app_config[config_name]
    except KeyError as e:
        print(
            f"[ ] Invalid config name {e}. Available configurations are: "
            f"{list(app_config.keys())}\n"
        )
        sys.exit(1)

    app.config.from_object(configuration)

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

    migrate.init_app(app, db)
    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)  # noqa

    admin = Admin(
        app,
        name="My App",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView(),
    )
    admin.add_view(DefaultModelView(Settings, db.session))
    admin.add_link(MenuLink(name="Logout", category="", url="/auth/logout?next=/admin"))

    #
    # dev static
    #

    @app.route("/devstatic/<path:boxormodule>/f/<path:filename>")
    def devstatic(boxormodule, filename):
        if app.config["DEBUG"]:
            module_static = os.path.join(modules_path, boxormodule, "static")
            return send_from_directory(module_static, filename=filename)

    available_everywhere_entities = {}

    #
    # load blueprints
    #
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
                    # print(f"[ ] {e}")
                    pass
                try:
                    mod_global = importlib.import_module(
                        f"{{ cookiecutter.project_slug }}.modules.{folder}.{sub_folder}.global"
                    )
                    available_everywhere_entities.update(
                        mod_global.available_everywhere
                    )
                except ImportError:
                    # print(f"[ ] {e}")
                    pass

        else:
            # apps
            try:
                mod = importlib.import_module(f"{{ cookiecutter.project_slug }}.modules.{folder}.view")
                app.register_blueprint(getattr(mod, f"{folder}_blueprint"))
            except AttributeError:
                pass
                # print("[ ] Blueprint skipped:", e)
            try:
                mod_global = importlib.import_module(f"{{ cookiecutter.project_slug }}.modules.{folder}.global")
                available_everywhere_entities.update(mod_global.available_everywhere)
            except ImportError:
                # print(f"[ ] {e}")
                pass
    #
    # custom templates folder
    #
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

    #
    # global vars
    #
    @app.context_processor
    def inject_global_vars():
        APP_NAME = get_setting("APP_NAME")

        base_context = {
            "APP_NAME": APP_NAME,
            "len": len,
            "current_user": current_user,
        }
        base_context.update(available_everywhere_entities)

        return base_context

    # end of func
    return app


with open(os.path.join(base_path, "config.json")) as f:
    config_json = json.load(f)

environment = config_json["environment"]
app = create_app(environment)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
