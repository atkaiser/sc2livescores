from fabric.api import local, settings, abort, run, cd

def prepare_deploy():
#     local("./manage.py test my_app")
    local("git add -p && git commit")
    local("git push origin master")

def deploy_prod():
    code_dir = '/home/sc2ls-dev/dev/sc2ls'
    with cd(code_dir):
        kill_prev()
        run("git pull")
        run("nohup manage.py runserver 0.0.0.0:3000 &")
        with cd('sc2game/utils'):
            run("nohup python update_state.py &")
        
def kill_prev():
    