# -*- coding: utf-8 -*-
import json
import requests
from pairwise_conflict_dataset import settings


class GithubAPI(object):

    @staticmethod
    def get_project_info(project):
        token = 'token {}'.format(settings.GITHUB_TOKEN)
        headers = {'Authorization': token}
        try:
            ret = requests.get(project.api_url, headers=headers)
            json_ret = json.loads(ret.content)
        except Exception as e:
            print(e)
            return {}
        return json_ret

    @staticmethod
    def get_pull_request_info(pull_request):
        url = '{}/pulls/{}'.format(pull_request.project.api_url, pull_request.github_id)
        token = 'token {}'.format(settings.GITHUB_TOKEN)
        headers = {'Authorization': token}
        try:
            ret = requests.get(url, headers=headers)
            json_ret = json.loads(ret.content)
        except Exception as e:
            print(e)
            return {}
        return json_ret
