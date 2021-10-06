# Copyright 2021 Expedient
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
from urllib.error import HTTPError


class Endgame(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.token = self.get_token()

  def get_token(self):
    url = f'https://{self.host}/api/v1/auth/login'
    data = {
      'username': self.username,
      'password': self.password
    }
    payload = dumps(data)
    response = open_url(url, data=payload, method='POST')
    auth_data = loads(response.read())
    return auth_data['metadata']['token']

  def send_api_request(self, endpoint, method, data=None):
    url = f'https://{self.host}/api/{endpoint}'
    payload = None
    if data:
      payload = dumps(data)

    response = open_url(url, data=payload, method=method)
    return loads(response.read())