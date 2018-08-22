import base64
import json
import os

import logging

from app.model import AnsiblePlaybookType


class AnsiblePlaybook(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    name = None
    inventory_group_name = None
    _extended_args = []

    def __init__(self, ansible_playbook_type: AnsiblePlaybookType, inventory_group_name: str = None):
        self.name = ansible_playbook_type.pb_name
        self.inventory_group_name = inventory_group_name

        for earg in ansible_playbook_type.ext_args:
            self._extended_args.append(f"-e {earg}")

    def get_extended_args(self):
        self.logger.debug("get_extended_args method")

    def get_limit(self):
        self.logger.debug("get_limit method")


class AnsiblePlaybookUpdateServerConnections(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _ip_addresses_list = []
    _vpn_type = None

    def __init__(self, vpn_type: str, ip_addresses_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vpn_type = vpn_type
        if ip_addresses_list:
            self._ip_addresses_list = ip_addresses_list

    def add_ip_address(self, ip: str):
        self.logger.debug(f"add_ip_address method {ip}")
        self._ip_addresses_list.append(ip)

    def add_ip_addresses(self, *ips):
        self.logger.debug(f"add_ip_addresses method {ips}")
        for ip in ips:
            self._ip_addresses_list.append(ip)

    def get_extended_args(self):
        return f'{"vpn" : "{self._vpn_type}"}'

    def get_limit(self):
        return f"'--limit {','.join(self._ip_addresses_list)}'"


class AnsiblePlaybookCreateVPNUser(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    _user_config_dir = '/tmp/dfnvpn_ansible'

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list

    def add_user(self, user_email: str):
        self.logger.debug(f"add_user method {user_email}")
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
        self.logger.debug(f"add_users method {user_emails}")
        for user in user_emails:
            self._user_email_list.append(user)

    def get_extended_args(self):
        client_list = []
        for user_email in self._user_email_list:
            client = {"name": user_email, "state": "present"}
            client_list.append(client)
        client_e_arg = {
            "clients": client_list
        }
        client_e_arg_str = json.dumps(client_e_arg)
        self._extended_args.append(f"-e {client_e_arg_str}")
        return self._extended_args

    def get_users_config_dict_base64(self) -> dict:
        self.logger.debug("get_users_config_dict_base64 method")
        data = {}
        for user_email in self._user_email_list:
            # TODO ikev2 config
            openvpn_config_path = f"{self._user_config_dir}/{user_email}.ovpn"
            self.logger.debug(f"work with {openvpn_config_path}")
            if os.path.isfile(openvpn_config_path):
                self.logger.debug(f"read file")
                file = open(openvpn_config_path, 'rb')
                file_content = file.read()
                file.close()

                self.logger.debug(f"create base64 string")
                config_base64_str = base64.b64encode(file_content).decode('ascii')
                data[user_email] = config_base64_str
                self.logger.debug(f"delete fil")
                os.remove(openvpn_config_path)
            else:
                self.logger.error(f"{openvpn_config_path} file not found!")
                self.logger.error(f"We did not get OpenVPN configuration file for user with email {user_email}")
                continue
        return data


class AnsiblePlaybookWithdrawVPNUser(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list

    def add_user(self, user_email: str):
        self.logger.debug(f"add_user method {user_email}")
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
        self.logger.debug(f"add_users method {user_emails}")
        for user in user_emails:
            self._user_email_list.append(user)

    def get_extended_args(self):
        client_list = []
        for user_email in self._user_email_list:
            client = {"name": user_email, "state": "absent"}
            client_list.append(client)
        client_e_arg = {
            "clients": client_list
        }
        client_e_arg_str = json.dumps(client_e_arg)
        self._extended_args.append(f"-e {client_e_arg_str}")
        return self._extended_args


class AnsiblePlaybookGetCRL(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnsiblePlaybookPutCRL(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
