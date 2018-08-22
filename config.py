class Config(object):
    DEBUG = False
    TESTING = False

    APP_SESSION_SK = 'mjePmctHGDjbaBYGbk7'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = APP_SESSION_SK
    TEMPLATES_AUTO_RELOAD = True

    VERSION = 'v1'
    API_BASE_URI = '/api/%s' % VERSION


class ProductionConfig(Config):
    ENV = 'production'

    ANSIBLE_CONFIG = {
        'root_path': '',
        'playbook_path': '',
        'inventory_file': '',
    }


class DevelopmentConfig(Config):
    ENV = 'development'

    DEBUG = True

    ANSIBLE_CONFIG = {
        'root_path': '',
        'playbook_path': '',
        'inventory_file': '',
    }


class TestingConfig(Config):
    ENV = 'testing'

    TESTING = True
    DEBUG = True

    ANSIBLE_CONFIG = {
        'root_path': '/opt/dfnvpn/playbooks',
        'playbook_path': '/opt/dfnvpn/playbooks',
        'inventory_file': '/etc/ansible/hosts',
    }
