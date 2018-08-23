from enum import Enum


class AnsiblePlaybookType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, pb_name, ext_args):
        self.sid = sid
        self.pb_name = pb_name
        self.ext_args = ext_args

    CREATE_VPN_USER = (1, 'pki.client.yml', [])
    WITHDRAW_VPN_USER = (2, 'pki.client.yml', [])
    UPDATE_SERVER_CONNECTIONS = (3, 'server_connections.yml', [])
    GET_CRL_FROM_SERVER = (4, 'update.crl.yml', ['{"get_crl" : "true"}'])
    UPDATE_CRL_FROM_SERVER = (5, 'update.crl.yml', ['{"put_crl" : "true"}'])
