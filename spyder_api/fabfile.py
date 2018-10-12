import os
import time
import datetime
from contextlib import contextmanager as _contextmanager

from functools import wraps

from fabric.api import *
from fabric.contrib import files
from fabric.decorators import hosts
from fabric.colors import yellow, green, blue


REPO_PATH = '/home/ravi/devel/gale-backend/spyder_api/'
DEVELOPMENT_BRANCH_NAME = 'master'
PROJECT_DIRECTORY = 'mcam'
LOCAL_FILES_PATH = '/home/ravi/localfiles'
REMOVE_OLD_DIRS = False

APP_DIRECTORY = 'mcam'

VENV_PATH = '/home/ravi/.virtualenvs/gale/bin/'

SERVICES_TO_START = ['gunicorn', 'celeryd', 'celeryworker']

SERVICES_TO_STOP = []

PRODUCTION_MAIN_SERVER = '139.59.59.123'
PRODUCTION_LOGIN_USERNAME = 'ravi'


def log_call(func):
    @wraps(func)
    def logged(*args, **kawrgs):
        header = "-" * len(func.__name__)
        print(green("\n".join([header, func.__name__, header]), bold=True))
        return func(*args, **kawrgs)
    return logged


@_contextmanager
def virtualenv():
    with prefix('source %s/activate' % VENV_PATH):
        yield


def deploy_on_test():
    # Configuration
    global REPO_PATH
    global VENV_PATH
    global APP_DIRECTORY
    REPO_PATH = '/home/ravi/devel/gale-backend'
    VENV_PATH = '/home/ravi/.virtualenvs/gale/bin'
    TEST_LOCAL_FILES_PATH = '/home/ravi/localfiles'
    TEST_DEPLOY_PATH = '/home/ravi/deploy'
    USER = 'ravi'
    USERGROUP = 'ravi'
    APP_DIRECTORY = 'spyder_api'

    with virtualenv():
        with cd(REPO_PATH):
            print('Moved to directory ' + blue(os.getcwd()))
            run('git fetch --all')
            run('git reset --hard origin/%s' % (DEVELOPMENT_BRANCH_NAME))
            run('git checkout %s' % (DEVELOPMENT_BRANCH_NAME))
            run('cp -f %s/* spyder_api/' % (TEST_LOCAL_FILES_PATH))
            run('pip install -r requirements.txt')

        with cd(TEST_DEPLOY_PATH):
            # run('pwd')
            today = datetime.datetime.now().strftime('%d%m%y')
            file_name = 'spyder_api' + today
            num = 1
            while files.exists('%s-%d' % (file_name, num)):
                num += 1
            print('Directory name would be: %s-%d' % (file_name, num))

            run('cp -r %s/spyder_api %s-%d' % (REPO_PATH, file_name, num))

            with cd('%s-%d/' % (file_name, num)):
                run('pwd')
                run('python manage.py migrate')
                run('python manage.py collectstatic --noinput')
                run('python manage.py invalidate_cache')

            run('rm %s/mcam' % (TEST_DEPLOY_PATH))
            run('ln -s %s/%s-%d mcam' % (TEST_DEPLOY_PATH, file_name, num))
            sudo('chown -R %s:%s .' % (USER, USERGROUP))
            sudo('systemctl daemon-reload')
            if SERVICES_TO_START:
                sudo('systemctl restart %s' % ' '.join(SERVICES_TO_START))
            if SERVICES_TO_STOP:
                sudo('systemctl stop %s' % ' '.join(SERVICES_TO_STOP))

            # sudo('systemctl restart gunicorn')
            # sudo('systemctl restart celeryd')
            # sudo('systemctl restart celeryworker')

            if REMOVE_OLD_DIRS:
                print('REMOVING OLD DIRECTORIES')
                sudo("ls --format 'single-column' -d */ | grep -v '^mcam/$\|^%s-%d/$' | xargs rm -rfv" % (
                    file_name, num))
            else:
                print('NOT REMOVING OLD DIRECTORIES')

            timestr = datetime.datetime.now().strftime(
                '%a, %d-%b-%Y %I:%M:%S ' + '%s' % (time.tzname[0]))
            print('Deployed at ' + yellow(timestr))


@task
@hosts('%s@%s' % (PRODUCTION_LOGIN_USERNAME, PRODUCTION_MAIN_SERVER))
def deploy_on_prod():
    global SERVICES_TO_START
    SERVICES_TO_START = ['gunicorn', 'celeryworker']
    global SERVICES_TO_STOP
    SERVICES_TO_STOP = ['celeryd']
    deploy_on_test()
