# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

from os.path import isdir, expanduser, join
from functools import wraps

from flask import Flask, request, jsonify

from datacats.environment import Environment, DatacatsError

MAIN_ENV_NAME = 'multisite'
MAIN_DATADIR_PATH = join(expanduser('~'), '.datacats', MAIN_ENV_NAME)
# HTTP status for when THEY messed up
CLIENT_ERROR_CODE = 409
# HTTP status for when WE messed up
SERVER_ERROR_CODE = 500
app = Flask(__name__)


def api_has_parameters(*keys):
    """
     Decorator that ensures that certain parameters exist and have sensible
     values (i.e. not empty, not None). If one of the keys isn't in the request
     parameters, an error will be returned.

     :param f: The function to be decorated
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*f_args):
            if all([key in request.form and request.form[key]
                    for key in keys]):
                # Let the function deal with it - valid
                return func(*f_args)
            else:
                return jsonify({
                   'error': 'One or more parameters missing. '
                   'Required parameters are: {}, supplied: {}'
                   .format(list(keys), request.args)
                }), CLIENT_ERROR_CODE

        return wrapper

    return decorator


def env_must_exist(func):
    """
    Wraps a Flask endpoint function and ensures that the main environment
    exists.
    """
    @wraps(func)
    def _check(*f_args):
        if isdir(MAIN_DATADIR_PATH):
            return func(*f_args)
        else:
            return jsonify({
                'error': 'Environment {} doesn\'t exist. Please follow setup '
                         'instructions.'.format(MAIN_ENV_NAME)
            }), CLIENT_ERROR_CODE
    return _check


def datacats_api_command(require_valid_child=False, *keys):
    """
    Wraps a function with safety measures to report a DatacatsError
    back in a 409 response.

    :param requires_valid_child True if an endpoint requires a child to exist
                                for it to be able to work.
    :param keys                 List of arguments that are required for this
                                environment shouldn't operate.
    """
    def decorator(func):
        @wraps(func)
        @api_has_parameters(*keys)
        @env_must_exist
        def wrapper():
            if 'name' not in request.form:
                child_name = None
            else:
                child_name = request.form.get('name')

            try:
                environment = Environment.load(MAIN_ENV_NAME, child_name)

                if require_valid_child:
                    environment.require_valid_child()

                return func(environment)
            except DatacatsError as e:
                return jsonify({'error': str(e)}), CLIENT_ERROR_CODE
        return wrapper
    return decorator



@app.route('/api/create', methods=['POST'])
@datacats_api_command(False, 'name')
def make_child(environment):
    environment.create_directories(create_project_dir=False)
    environment.start_postgres_and_solr()
    environment.fix_storage_permissions()
    environment.fix_project_permissions()
    environment.ckan_db_init()
    environment.start_web()

    return jsonify({'success': 'Child environment {} created.'
                    .format(environment.child_name)})


@app.route('/api/start', methods=['POST'])
@datacats_api_command(True, 'name')
def start_child(environment):
    environment.start_postgres_and_solr()
    environment.start_web()

    return jsonify({'success': 'Child environment {} started.'
                    .format(environment.child_name)})



@app.route('/api/purge', methods=['POST'])
@datacats_api_command(True, 'name')
def purge_child(environment):
    environment.stop_web()
    environment.stop_postgres_and_solr()
    environment.purge_data([environment.child_name], never_delete=True)

    return jsonify({'success': 'Child environment {} purged.'
                    .format(environment.child_name)})


@app.route('/api/stop', methods=['POST'])
@datacats_api_command(True, 'name')
def stop_child(environment):
    environment.stop_web()
    environment.stop_postgres_and_solr()

    return jsonify({'success': 'Child environment {} stopped.'
                    .format(environment.child_name)})


@app.route('/api/status', methods=['POST'])
@datacats_api_command(True, 'name')
def child_status(environment):
    return jsonify({
        'default_port': str(environment.port),
        'name': environment.child_name,
        'containers_running': ' '.join(environment.containers_running())
    })


@app.route('/api/list', methods=['POST'])
@datacats_api_command()
def list_children(environment):
    return jsonify({'children': environment.children})


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
