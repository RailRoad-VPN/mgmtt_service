import base64
import calendar
import logging
import os
import shutil
import time
import uuid
from datetime import datetime

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='MGMT_SERVICE get_config_script: %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("get_config_script")

def gen_sec_token() -> str:
    token = ""
    ruuid = str(uuid.uuid4())
    ruuid = ruuid.replace("-", "")
    ruuid_len = len(ruuid)
    r4 = str(random_x(1, ruuid_len))
    token += ruuid
    unixtime = get_unixtime()
    unixtime_divided = int(unixtime) / int(r4)
    unixtime_divided_rounded = "%.10f" % (unixtime_divided)
    unixtime_divided_len = str(len(str(unixtime_divided_rounded)))
    if len(unixtime_divided_len) == 1:
        unixtime_divided_len = "0" + str(unixtime_divided_len)
    left_token = token[:int(r4)]
    center_token = str(unixtime_divided_rounded)
    right_token = token[int(r4):]
    token = left_token + center_token + right_token
    if len(r4) == 1:
        r4 = "0" + str(r4)
    token = str(r4) + str(unixtime_divided_len) + token
    return token


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    from random import randint
    return randint(range_start, range_end)


def random_x(minX, maxX):
    import random
    return random.randint(minX, maxX)


def get_unixtime() -> int:
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime

DIRECTORY_TO_WATCH = "/tmp/dfnvpn_ansible"


# DIRECTORY_TO_WATCH = "./dfn"


class Watcher:

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.debug(f"{self.__class__}: Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event, **kwargs):
        if event.event_type == 'created':
            logger.debug("Received created event - %s." % event.src_path)
            process_file(event.src_path)


class VPNConfig:
    file_path = None
    config_base64 = None

    vpn_type = None
    platform = None
    email = None
    file_extension = None

    api_host = "https://api.rroadvpn.net"
    # api_host = "http://127.0.0.1:8000"
    resource_uri = "api/v1/users/<string:user_id>/servers/all/configurations"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }

    def __init__(self, file_path):
        logger.debug(f"process file {file_path}")
        self.file_path = file_path

        file_name = self.file_path.split("/")[-1]
        self.vpn_type = file_name.split("_")[0]
        logger.debug(f"vpn_type_text: {self.vpn_type}")
        self.platform = file_name.split("_")[1]
        logger.debug(f"platform_text: {self.platform}")
        self.email = ".".join(file_name.split("_")[2].split(".")[0:-1])
        logger.debug(f"email: {self.email}")
        self.file_extension = file_name.split("_")[2].split(".")[-1]
        logger.debug(f"file_extension: {self.file_extension}")

        if self.file_extension == "retry":
            self.unmark_retry()

    def process_config_file(self):
        logger.debug(f"{self.__class__}: process_config_file {self.file_path}")
        config_file = open(self.file_path, 'rb')
        config_file_content = config_file.read()
        logger.debug(f"{self.__class__}: create base64 string")
        self.config_base64 = base64.b64encode(config_file_content).decode('ascii')
        logger.debug(f"{self.__class__}: close file {self.file_path}")
        config_file.close()

    def send(self):
        logger.debug(f"{self.__class__}: v method")
        url = f"{self.api_host}/{self.resource_uri.replace('<string:user_id>', self.email)}"

        data = {
            'config_base64': self.config_base64,
            'vpn_type': self.vpn_type,
            'platform': self.platform,
        }

        self.headers['X-Auth-Token'] = gen_sec_token()

        try:
            resp = requests.post(url=url, json=data, headers=self.headers)
            logger.debug(f"API Response: {resp}")
            return resp.ok
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"API error: {e}")

    def mark_retry(self):
        logger.debug(f"{self.__class__}: mark_retry method")
        shutil.move(self.file_path, f"{self.file_path}.retry")

    def unmark_retry(self):
        logger.debug(f"{self.__class__}: unmark_retry method")
        nfile_path = ".".join(self.file_path.split(".")[0:-1])
        shutil.move(self.file_path, f"{nfile_path}")
        self.file_path = nfile_path

    def delete(self):
        logger.debug(f"{self.__class__}: delete file {self.file_path}")
        os.remove(self.file_path)


def process_file(config_file_name):
    if config_file_name.split(".")[-1] != 'ovpn':
        logger.debug("no ovpn file. pass")
        return
    # config_file_path = DIRECTORY_TO_WATCH + config_file_name
    config_file_path = config_file_name
    vpn_config = VPNConfig(file_path=config_file_path)
    is_ok = vpn_config.send()
    if not is_ok:
        logger.debug("HALT! API Response IS NOT OK! Need retry! Mark file.")
    else:
        logger.debug("API Response IS OK! Delete file.")
        vpn_config.delete()


if __name__ == '__main__':
    data = {}

    # TODO some logic to retry for retry files

    # process existed files on launch script moment
    config_file_name_list = os.listdir(DIRECTORY_TO_WATCH)
    for config_file_name in config_file_name_list:
        process_file(config_file_name=config_file_name)

    w = Watcher()
    w.run()
