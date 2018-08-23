import logging
import os
import sys
from http import HTTPStatus

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from app.service import AnsibleService, VPNMGMTService

sys.path.insert(1, '../rest_api_library')
from response import make_error_request_response
from api import register_api

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logger.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logger.info("Config name: %s" % config_name)
app.config.from_object(config_name)

app_config = app.config
api_base_uri = app_config['API_BASE_URI']

auth = HTTPBasicAuth()

data = app.config['BASIC_AUTH']


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    if username == data['username'] and password == data['password']:
        return True


ansible_service = AnsibleService(ansible_inventory_file=app_config['ANSIBLE_CONFIG']['inventory_file'],
                                 ansible_path=app_config['ANSIBLE_CONFIG']['root_path'],
                                 ansible_playbook_path=app_config['ANSIBLE_CONFIG']['playbook_path'])

vpn_mgmt_service = VPNMGMTService(ansible_service=ansible_service)

from app.resources.vpns.mgmt.users import VPNSMGMTUsersAPI
from app.resources.vpns.mgmt.vpns.servers.connections import MGMTVPNSServersConnections

apis = [
    {'cls': VPNSMGMTUsersAPI, 'args': [vpn_mgmt_service, app_config]},
    {'cls': MGMTVPNSServersConnections, 'args': [vpn_mgmt_service, app_config]},
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
