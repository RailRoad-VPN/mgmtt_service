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
        self.logger.debug("ansible Root Path: " + ansible_path)
        self.logger.debug("ansible inventory file: " + ansible_inventory_file)
        self.logger.debug("ansible Playbooks Path: " + ansible_playbook_path)

        self.logger.debug("create ansible command with out arguments")
        self._cmd_wo_args = f"ansible-playbook {ansible_path}/{ansible_playbook_path}/" + "{pb_name}"
        if ansible_inventory_file is not None:
            self._cmd_wo_args += f" -i {ansible_inventory_file} "

        self.logger.info("base ansible shell command: " + self._cmd_wo_args)

    def exec_playbook(self, ansible_playbook: AnsiblePlaybook, is_async: bool = False) -> int:
        name = ansible_playbook.name
        inventory = ansible_playbook.inventory_group_name
        ext_args = ansible_playbook.get_extended_args()
        self.logger.debug(f"playbook Name: {name}")
        self.logger.debug(f"inventory Group: {inventory}")
        self.logger.debug(f"args: {ext_args}")

        cmd = self._cmd_wo_args
        self.logger.debug(cmd)
        if ansible_playbook.inventory_group_name is not None:
            cmd += f"-l  {ansible_playbook.inventory_group_name}" + " -f 1 "
        cmd = cmd.format(pb_name=ansible_playbook.name)
        self.logger.debug(cmd)

        for e_arg in ansible_playbook.get_extended_args():
            cmd += f" {e_arg} "
        self.logger.debug(cmd)

        cmd += ansible_playbook.get_vault(path_to_vault=f"{self.ansible_root_path}/{self.ansible_playbook_path}")
        self.logger.debug(f"final cmd: {cmd}")

        self.logger.info("execute ansible shell command")
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p.communicate()

        if not is_async:
            p_status = p.wait()
            if output is not None:
                self.logger.error(f"execute ansible playbook {name} output: {output}")
            if err is not None:
                self.logger.error(f"execute ansible playbook {name} error: {err}")
                return 9090909090
            if p_status is not None:
                try:
                    p_status = int(p_status)
                    self.logger.debug(f"execute ansible playbook {name} status: {p_status}")
                except KeyError:
                    self.logger.info(f"exec ansible playbook {name} return code: {p_status}")
                return p_status
            return 9090909090
        else:
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

    def create_vpn_user(self, user_email: str) -> str:
        self.logger.debug(f"create_vpn_user method with parameters user_email: {user_email}")
        self.logger.debug("create ansible playbook to create VPN user")
        apcvu = AnsiblePlaybookCreateVPNUser(ansible_playbook_type=AnsiblePlaybookType.CREATE_VPN_USER)
        self.logger.debug("add user email")
        apcvu.add_user(user_email=user_email)
        self.logger.debug("call ansible service")
        code = self._ansible_service.exec_playbook(ansible_playbook=apcvu)
        self.logger.debug("check code")
        if code == 0:
            self.logger.debug("code OK")
            # TODO забрать конифг по пути /tmp/dfnvpn_ansible/<email>.ovpn
            user_config_dict = apcvu.get_users_config_dict_base64()
            return user_config_dict.get(user_email)
        else:
            self.logger.debug("failed to create VPN user")
            err = VPNMGMTError.ANSIBLE_CREATE_USER_VPN_USER_ERROR
            raise AnsibleException(error=err.message, error_code=err.code, developer_message=err.developer_message)

    '''
        withdaw user certificate on PKI infrastructure server and withdraw in on every server
    '''

    def withdraw_vpn_user(self, user_email: str):
        self.logger.debug(f"withdraw_vpn_user method with parameters user_email: {user_email}")
        self.logger.debug("create ansible playbook to withdraw VPN user")
        apcvu = AnsiblePlaybookWithdrawVPNUser(ansible_playbook_type=AnsiblePlaybookType.WITHDRAW_VPN_USER)
        self.logger.debug("add user email")
        apcvu.add_user(user_email=user_email)
        self.logger.debug("call ansible service")
        code = self._ansible_service.exec_playbook(ansible_playbook=apcvu, is_async=False)
        self.logger.debug("check code")
        if code == 0:
            self.logger.debug("code OK")
            self.logger.debug("create ansible playbook to get updated CRL from PKI server")
            apgc = AnsiblePlaybookGetCRL()
            self.logger.debug("call ansible service")
            code = self._ansible_service.exec_playbook(ansible_playbook=apgc, is_async=False)
            self.logger.debug("check code")
            if code == 0:
                self.logger.debug("code OK")
                self.logger.debug("create ansible playbook to update CRL on every VPN server")
                appc = AnsiblePlaybookPutCRL()
                self.logger.debug("call ansible service")
                self._ansible_service.exec_playbook(ansible_playbook=appc, is_async=True)
            else:
                self.logger.error("failed to update CRL on every VPN server")
        else:
            self.logger.error("failed to get updated CRL from PKI server")

    '''
        retrieve connections information from every VPN server (call scripts)
    '''

    def update_server_connections(self, server_ip_list: List[str], vpn_type_name: str):
        self.logger.debug(f"create ansible playbook to update server connections depends on list: {server_ip_list}")
        apusc = AnsiblePlaybookUpdateServerConnections(
            ansible_playbook_type=AnsiblePlaybookType.UPDATE_SERVER_CONNECTIONS, ip_addresses_list=server_ip_list,
            vpn_type=vpn_type_name)
        self.logger.debug("call ansible service")
        code = self._ansible_service.exec_playbook(ansible_playbook=apusc)
        if code != 0:
            err = VPNMGMTError.ANSIBLE_UPDATE_SERVER_CONNECTIONS_ERROR
            raise AnsibleException(error=err.message, error_code=err.code, developer_message=err.developer_message)
