import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='MGMT_SERVICE get_config_script: %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("get_config_script")


class Watcher:
    DIRECTORY_TO_WATCH = "/tmp/dfnvpn_ansible"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.debug("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event, **kwargs):
        logger.debug(f"{event.event_type}")
        if event.event_type == 'created':
            logger.debug("Received created event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()
