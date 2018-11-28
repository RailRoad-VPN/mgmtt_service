import subprocess
from typing import List

from app.model.ansible_playbooks import *
from app.model.exception import AnsibleException, VPNMGMTError


class AnsibleService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    ansible_root_path = None
    ansible_playbook_path = None

    _cmd_wo_args = None

    def __init__(self, ansible_path: str, ansible_inventory_file: str, ansible_playbook_path: str):
        self.ansible_root_path = ansible_path
        self.ansible_playbook_path = ansible_playbook_path
        self.logger.debug(f"{self.__class__}: ansible Root Path: " + ansible_path)
        self.logger.debug(f"{self.__class__}: ansible inventory file: " + ansible_inventory_file)
        self.logger.debug(f"{self.__class__}: ansible Playbooks Path: " + ansible_playbook_path)

        self.logger.debug(f"{self.__class__}: create ansible command with out arguments")
        self._cmd_wo_args = f"/usr/bin/ansible-playbook {ansible_path}/{ansible_playbook_path}/" + "{pb_name}"
        if ansible_inventory_file is not None:
            self._cmd_wo_args += f" -i {ansible_inventory_file} "

        self.logger.info("base ansible shell command: " + self._cmd_wo_args)

    def exec_playbook(self, ansible_playbook: AnsiblePlaybook, is_async: bool = False) -> int:
        name = ansible_playbook.name
        inventory = ansible_playbook.inventory_group_name
        ext_args = ansible_playbook.get_extended_args()
        self.logger.debug(f"{self.__class__}: playbook Name: {name}")
        self.logger.debug(f"{self.__class__}: inventory Group: {inventory}")
        self.logger.debug(f"{self.__class__}: args: {ext_args}")

        cmd = self._cmd_wo_args
        self.logger.debug(cmd)
        if inventory is not None:
            cmd += f" -l  {inventory}" + " -f 1 "
        cmd = cmd.format(pb_name=ansible_playbook.name)
        self.logger.debug(cmd)

        for e_arg in ext_args:
            cmd += f" {e_arg} "
        self.logger.debug(cmd)

        vault = ansible_playbook.get_vault(path_to_vault=f"{self.ansible_root_path}/{self.ansible_playbook_path}")
        cmd += f" {vault} "
        self.logger.debug(cmd)

        limit = ansible_playbook.get_limit()
        if limit:
            cmd += f" {limit} "
            self.logger.debug(cmd)

        # cmd = f"/bin/su dfnadm -c \"{cmd}\""
        cmd = f"{cmd}"

        self.logger.debug(f"{self.__class__}: final cmd: {cmd}")

        self.logger.info("execute ansible shell command")

        if not is_async:
            self.logger.info("execute in SYNC mode")
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (output, err) = p.communicate()
            p_status = p.wait()
            if output is not None:
                self.logger.error(f"execute ansible playbook {name} output: {output}")
            if err is not None:
                self.logger.error(f"execute ansible playbook {name} error: {err}")
            if p_status is not None:
                try:
                    p_status = int(p_status)
                    self.logger.debug(f"{self.__class__}: execute ansible playbook {name} status: {p_status}")
                except KeyError:
                    self.logger.info(f"exec ansible playbook {name} return code: {p_status}")
                return p_status
            return 9090909090
        else:
            self.logger.info("execute in ASYNC mode")
            subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None)
            return 0


class VPNMGMTService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _ansible_service = None

    def __init__(self, ansible_service: AnsibleService):
        self._ansible_service = ansible_service

    '''
        generate user certificate on PKI infrastructure server and register it on every server
    '''

    def create_vpn_user(self, user_email: str) -> None:
        self.logger.debug(f"{self.__class__}: create_vpn_user method with parameters user_email: {user_email}")
        self.logger.debug(f"{self.__class__}: create ansible playbook to create VPN user")
        apcvu = AnsiblePlaybookCreateVPNUser(ansible_playbook_type=AnsiblePlaybookType.CREATE_VPN_USER)
        self.logger.debug(f"{self.__class__}: add user email")
        apcvu.add_user(user_email=user_email)
        self.logger.debug(f"{self.__class__}: call ansible service")
        self._ansible_service.exec_playbook(ansible_playbook=apcvu, is_async=True)

    '''
        withdaw user certificate on PKI infrastructure server and withdraw in on every server
    '''

    def withdraw_vpn_user(self, user_email: str):
        self.logger.debug(f"{self.__class__}: withdraw_vpn_user method with parameters user_email: {user_email}")
        self.logger.debug(f"{self.__class__}: create ansible playbook to withdraw VPN user")
        apcvu = AnsiblePlaybookWithdrawVPNUser(ansible_playbook_type=AnsiblePlaybookType.WITHDRAW_VPN_USER)
        self.logger.debug(f"{self.__class__}: add user email")
        apcvu.add_user(user_email=user_email)
        self.logger.debug(f"{self.__class__}: call ansible service")
        code = self._ansible_service.exec_playbook(ansible_playbook=apcvu, is_async=True)
        self.logger.debug(f"{self.__class__}: check code")
        if code == 0:
            self.logger.debug(f"{self.__class__}: code OK")
            self.logger.debug(f"{self.__class__}: create ansible playbook to get updated CRL from PKI server")
            apgc = AnsiblePlaybookGetCRL()
            self.logger.debug(f"{self.__class__}: call ansible service")
            code = self._ansible_service.exec_playbook(ansible_playbook=apgc, is_async=True)
            self.logger.debug(f"{self.__class__}: check code")
            if code == 0:
                self.logger.debug(f"{self.__class__}: code OK")
                self.logger.debug(f"{self.__class__}: create ansible playbook to update CRL on every VPN server")
                appc = AnsiblePlaybookPutCRL()
                self.logger.debug(f"{self.__class__}: call ansible service")
                self._ansible_service.exec_playbook(ansible_playbook=appc, is_async=True)
            else:
                self.logger.error("failed to update CRL on every VPN server")
        else:
            self.logger.error("failed to get updated CRL from PKI server")

    '''
        retrieve connections information from every VPN server (call scripts)
    '''

    def update_server_connections(self, servers_group: str):
        self.logger.debug(
            f"{self.__class__}: create ansible playbook to update server connections depends on list: {servers_group}")
        apusc = AnsiblePlaybookUpdateServerConnections(
            ansible_playbook_type=AnsiblePlaybookType.UPDATE_SERVER_CONNECTIONS, servers_group=servers_group)
        self.logger.debug(f"{self.__class__}: call ansible service")
        code = self._ansible_service.exec_playbook(ansible_playbook=apusc, is_async=True)
        if code != 0:
            err = VPNMGMTError.ANSIBLE_UPDATE_SERVER_CONNECTIONS_ERROR
            raise AnsibleException(error=err.message, error_code=err.code, developer_message=err.developer_message)
