import logging
import os
import sys
from http import HTTPStatus

from flask import Flask, request

from app.resources.vpns.mgmt.users import VPNSMGMTUsersAPI
from app.resources.vpns.mgmt.vpns.servers.connections import MGMTVPNSServersConnections
from app.service import AnsibleService

sys.path.insert(1, '../rest_api_library')
from response import make_error_request_response
from api import register_api

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logging.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logging.info("Config name: %s" % config_name)
app.config.from_object(config_name)


app_config = app.config
api_base_uri = app_config['API_BASE_URI']

ansible_service = AnsibleService(ansible_inventory_file=app_config['ANSIBLE_CONFIG']['inventory_file'],
                                 ansible_path=app_config['ANSIBLE_CONFIG']['root_path'],
                                 ansible_playbook_path=app_config['ANSIBLE_CONFIG']['playbook_path'])

apis = [
    {'cls': VPNSMGMTUsersAPI, 'args': [ansible_service, app_config]},
    {'cls': MGMTVPNSServersConnections, 'args': [ansible_service, app_config]},
]

register_api(app, api_base_uri, apis)


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']


@app.errorhandler(400)
def not_found_error(error):
    return make_error_request_response(HTTPStatus.BAD_REQUEST)


@app.errorhandler(404)
def not_found_error(error):
    return make_error_request_response(HTTPStatus.NOT_FOUND)


@app.errorhandler(500)
def internal_error(error):
    return make_error_request_response(HTTPStatus.INTERNAL_SERVER_ERROR)
