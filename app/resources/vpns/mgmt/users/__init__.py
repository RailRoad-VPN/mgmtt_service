import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app import auth
from app.model.exception import AnsibleException
from app.service import VPNMGMTService

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from rest import APIResourceURL
from response import APIResponseStatus, APIResponse
from response import make_api_response


class VPNSMGMTUsersAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/mgmt/users/<string:user_email>'

    _config = None

    _vpn_mgmt_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNSMGMTUsersAPI.__api_url__}"
        api_urls = [
            # TODO put to update certificate
            APIResourceURL(base_url=url, resource_name='', methods=['POST', 'DELETE']),
        ]
        return api_urls

    def __init__(self, vpn_mgmt_service: VPNMGMTService, *args) -> None:
        super().__init__(*args)
        self._vpn_mgmt_service = vpn_mgmt_service

    @auth.login_required
    def post(self, user_email: str) -> Response:
        self.logger.debug('post method')

        try:
            self._vpn_mgmt_service.create_vpn_user(user_email=user_email)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp
        except AnsibleException as e:
            self.logger.error(e)
            error_code = e.error_code
            error = e.error
            developer_message = e.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(data=response_data, http_code=http_code)
            return resp

    @auth.login_required
    def delete(self, user_email: str):
        self.logger.debug('post method')

        try:
            self._vpn_mgmt_service.withdraw_vpn_user(user_email=user_email)

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp
        except AnsibleException as e:
            self.logger.error(e)
            error_code = e.error_code
            error = e.error
            developer_message = e.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(data=response_data, http_code=http_code)
            return resp
