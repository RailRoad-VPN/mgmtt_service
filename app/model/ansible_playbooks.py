import base64
import json
import logging
import os

from app.model import AnsiblePlaybookType
from app.model.vpn_conf_platform import VPNConfigurationPlatform
from app.model.vpn_type import VPNType


class AnsiblePlaybook(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    name = None
    inventory_group_name = None
    args = None
    _extended_args = []

    def __init__(self, ansible_playbook_type: AnsiblePlaybookType, inventory_group_name: str = None):
        self.name = ansible_playbook_type.text
        self.inventory_group_name = inventory_group_name

        for earg in ansible_playbook_type.ext_args:
            self._extended_args.append(f"-e {earg}")
        else:
            self._extended_args = []

    def get_vault(self, path_to_vault: str):
        self.logger.debug(f"{self.__class__}: get_vault method")
        vault_arg = f'--vault-password-file={path_to_vault}/vault.txt'
        self.logger.debug(f"{self.__class__}: vault_arg: {vault_arg}")
        return vault_arg

    def get_extended_args(self):
        self.logger.debug(f"{self.__class__}: get_extended_args method")

    def get_limit(self):
        self.logger.debug(f"{self.__class__}: get_limit method")


class AnsiblePlaybookUpdateServerConnections(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _servers_group = None
    _vpn_type = None

    def __init__(self, vpn_type: str, ip_addresses_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vpn_type = vpn_type
        if ip_addresses_list:
            self._servers_group = ip_addresses_list

    def get_extended_args(self):
        return ["-e '{\"vpn\" : \"%s\"}'" % self._vpn_type, ]

    def get_limit(self):
        return f"--limit '{self._servers_group}'"


class AnsiblePlaybookCreateVPNUser(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list
        else:
            self._user_email_list = []

    def add_user(self, user_email: str):
        self.logger.debug(f"{self.__class__}: add_user method {user_email}")
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
        self.logger.debug(f"{self.__class__}: add_users method {user_emails}")
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
        e_args = self._extended_args
        e_args.append(f" -e '{client_e_arg_str}' ")
        return e_args

    def get_limit(self):
        return []


class AnsiblePlaybookWithdrawVPNUser(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _user_email_list = []

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list
        else:
            self._user_email_list = []

    def add_user(self, user_email: str):
        self.logger.debug(f"{self.__class__}: add_user method {user_email}")
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
        self.logger.debug(f"{self.__class__}: add_users method {user_emails}")
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
        self._extended_args.append(f" -e {client_e_arg_str} ")
        return self._extended_args

    def get_limit(self):
        return []


class AnsiblePlaybookGetCRL(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_extended_args(self):
        return []

    def get_limit(self):
        return []


class AnsiblePlaybookPutCRL(AnsiblePlaybook):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_extended_args(self):
        return []

    def get_limit(self):
        return []
