# -*- coding: utf-8 -*-
import json
import requests
from requests.auth import HTTPBasicAuth

class GITHUBAPI(object):

    def __init__(self, owner, repo):
        self.owner = owner 
        self.repo = repo

    def get_pull_request_info(self, pull_request_id):
        url = 'https://api.github.com/repos/{}/{}/pulls/{}'.format(self.owner, self.repo, pull_request_id)
        token = 'token 9767f1c10603cf6a0ce5423bbe016b938b268451'
        headers = {'Authorization': token}
        try:
            ret = requests.get(url, headers=headers)
            json_ret = json.loads(ret.content)
        except Exception as e:
            print(e)
            return {}
        return json_ret