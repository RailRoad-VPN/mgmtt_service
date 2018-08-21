import logging
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.model.exception import *
from app.service import VPNMGMTService

sys.path.insert(1, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL


class MGMTVPNSServersConnections(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/servers/connections'

    _config = None

    _vpn_mgmt_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{MGMTVPNSServersConnections.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='update', methods=['POST'])
        ]
        return api_urls

    def __init__(self, vpnmgmt_service: VPNMGMTService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._vpn_mgmt_service = vpnmgmt_service

    def post(self) -> Response:
        self.logger.debug('post method')

        self.logger.debug('check JSON in request')
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=VPNCError.REQUEST_NO_JSON)

        self.logger.debug('get list of IP addresses from request')
        ip_list = request_json.get('ip_list')

        try:
            is_ok = self._vpn_mgmt_service.update_server_connections(server_ip_list=ip_list)

            if is_ok:
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            else:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST)
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