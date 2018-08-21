import json

from app.model import AnsiblePlaybookType


class AnsiblePlaybook(object):
    __version__ = 1

    name = None
    inventory_group_name = None
    _extended_args = []

    def __init__(self, ansible_playbook_type: AnsiblePlaybookType, inventory_group_name: str = None):
        self.name = ansible_playbook_type.pb_name
        self.inventory_group_name = inventory_group_name

        for earg in ansible_playbook_type.ext_args:
            self._extended_args.append(f"-e {earg}")

    def get_extended_args(self):
        pass


class AnsiblePlaybookUpdateServerConnections(AnsiblePlaybook):
    __version__ = 1

    _ip_addresses_list = []

    def __init__(self, ip_addresses_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if ip_addresses_list:
            self._ip_addresses_list = ip_addresses_list

    def add_ip_address(self, ip: str):
        self._ip_addresses_list.append(ip)

    def add_ip_addresses(self, *ips):
        for ip in ips:
            self._ip_addresses_list.append(ip)

    def get_extended_args(self):
        earg = f"ip_list={','.join(self._ip_addresses_list)}"
        self._extended_args.append(f"-e {earg}")
        return self._extended_args


class AnsiblePlaybookCreateVPNUser(AnsiblePlaybook):
    __version__ = 1

    _user_email_list = []

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list

    def add_user(self, user_email: str):
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
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


class AnsiblePlaybookWithdrawVPNUser(AnsiblePlaybook):
    __version__ = 1

    _user_email_list = []

    def __init__(self, user_email_list: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if user_email_list:
            self._user_email_list = user_email_list

    def add_user(self, user_email: str):
        self._user_email_list.append(user_email)

    def add_users(self, *user_emails):
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

    _user_email_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnsiblePlaybookPutCRL(AnsiblePlaybook):
    __version__ = 1

    _user_email_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
