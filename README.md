# shopyo-factory

A Flask based full stack application template. To see the modules included visit
the [shopyo docs](https://shopyo.readthedocs.io/en/latest/modules.html#default-modules-boxes)


## Usage

* Setup the new project

    ```
    $ python -m pip install --upgrade cookiecutter
    $ cookiecutter https://github.com/shopyo/shopyo-factory
    ```

* Setup and activate the virtual env

    For Linux:

    ```
    $ cd {PROJECT_NAME}
    $ python3 -m venv env
    $ . env/bin/activate
    ```

    For Windows:

    ```
    > py -3 -m venv env
    > env\Scripts\activate
    ```
* Upgrade pip and setuptools:

    ```
    $ python -m pip install --upgrade pip setuptools
    ```

* Install the development and production requirements:

    ```
    $ pip install -r requirements/dev.txt && pip install -e .
    ```

* Initialize the app by running:

    ```
    $ cd {PROJECT_NAME}
    $ python manage.py initialise
    ```

* Run the app locally

    ```
    $ python manage.py run
    ```

* Go to the link http://127.0.0.1:5000/ and you should see `SITE UNDER CONSTRUCTION`. 
Go to http://127.0.0.1:5000/auth/login and then you can access the dashboard by logging 
in with email `admin@domain.com` and password `pass`
