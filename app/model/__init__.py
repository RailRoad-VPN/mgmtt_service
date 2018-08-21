from enum import Enum


class AnsiblePlaybookType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, pb_name, args, ext_args):
        self.sid = sid
        self.pb_name = pb_name
        self.args = args
        self.ext_args = ext_args

    CREATE_VPN_USER = (1, 'pki.client.yml', ['--vault-password-file=vault.txt'], [])
    WITHDRAW_VPN_USER = (2, 'pki.client.yml', ['--vault-password-file=vault.txt'], [])
    UPDATE_SERVER_CONNECTIONS = (3, 'server_connections.yml', ['--vault-password-file=vault.txt'], ['{"vpn" : "ipsec"}'])
    GET_CRL_FROM_SERVER = (4, 'update.crl.yml', ['--vault-password-file=vault.txt'], ['{"get_crl" : "true"}'])
    UPDATE_CRL_FROM_SERVER = (5, 'update.crl.yml', ['--vault-password-file=vault.txt'], ['{"put_crl" : "true"}'])
