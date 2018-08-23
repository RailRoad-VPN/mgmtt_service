import sys

sys.path.insert(0, '../rest_api_library')
from response import APIErrorEnum

name = 'MGMT-'
i = 0


def count():
    global i
    i += 1
    return i


class VPNMGMTError(APIErrorEnum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    UNKNOWN_ERROR_CODE = (name + str(count()), 'UNKNOWN_ERROR_CODE phrase', 'UNKNOWN_ERROR_CODE description')

    REQUEST_NO_JSON = (name + str(count()),  'REQUEST_NO_JSON phrase', 'REQUEST_NO_JSON description')

    ANSIBLE_CREATE_USER_VPN_USER_ERROR = (name + str(count()),  'ANSIBLE_CREATE_USER_VPN_USER_ERROR phrase', 'ANSIBLE_CREATE_USER_VPN_USER_ERROR description')
    ANSIBLE_UPDATE_SERVER_CONNECTIONS_ERROR = (name + str(count()),  'ANSIBLE_UPDATE_SERVER_CONNECTIONS_ERROR phrase', 'ANSIBLE_UPDATE_SERVER_CONNECTIONS_ERROR description')


class VPNMGMTException(Exception):
    __version__ = 1

    error = None
    error_code = None
    developer_message = None

    def __init__(self, error: str, error_code: int, developer_message: str = None, *args):
        super().__init__(*args)
        self.error = error
        self.error_code = error_code
        self.developer_message = developer_message


class VPNMGMTNotFoundException(VPNMGMTException):
    __version__ = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnsibleException(VPNMGMTException):
    __version__ = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
