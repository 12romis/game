import sys

from fabric.api import run, env, local, sudo, prefix, task, cd
from fabric.operations import put
from fabric.context_managers import shell_env

# run production deploy with command "fab prod deploy"
# run qa deploy with command "fab test deploy"

def clean():
    with cd(env.path):
        run('find . -name "*.pyc" -exec rm -f {} \;')


@task
def restart():
    sudo('service spila restart')


@task
def update():
    with cd(env.path):
        # run('git checkout {}'.format(env.branch))
        run('git stash')
        run('git pull origin {}'.format(env.branch))
        with prefix('source /var/www/html/python/dj2/bin/activate'):
            run('pip install -r requirements.txt')
            run('python manage.py migrate')
            run('python manage.py collectstatic --noinput')
    # for logs permission fix
    with cd('{}/logs'.format(env.path)):
        sudo('chmod g+w,o+w -R .')
    # sudo('service spila restart')


@task
def deploy():
    """ Update and restart """
    clean()
    update()
    restart()


@task
def prod():
    env.hosts = ['213.159.213.7']
    env.branch = 'master'
    env.user = 'root'
    env.password = 'Kz9QFQ7kWHvh'
    env.path = '/var/www/html/python/dj2/spila_dir/spila_server'

