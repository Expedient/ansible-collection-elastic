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

class Elastic(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')

  def send_api_request(self, endpoint, method, data=None):
    url = f'https://{self.host}:{self.port}/{endpoint}'
    headers = {}
    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    try:
      response = open_url(url, data=payload, method=method, validate_certs=self.validate_certs, headers=headers,
                          force_basic_auth=True, url_username=self.username, url_password=self.password)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.read())

  ## get_users() and get_user() support the native realm only
  def get_users(self):
    endpoint = '_security/user'
    return self.send_api_request(endpoint, 'GET')

  def get_user(self, username):
    endpoint = f'_security/user/{username}'
    return self.send_api_request(endpoint, 'GET')[username]

  def get_roles(self):
    endpoint = '_security/role'
    return self.send_api_request(endpoint, 'GET')

  def get_role(self, role_name):
    endpoint = f'_security/role/{role_name}'
    return self.send_api_request(endpoint, 'GET')

  def get_role_mappings(self):
    endpoint = '_security/role_mapping'
    return self.send_api_request(endpoint, 'GET')

  def get_role_mapping(self, role_mapping_name):
    endpoint = f'_security/role_mapping/{role_mapping_name}'
    return self.send_api_request(endpoint, 'GET')

  ## pipelines are returned as a dictionary with the pipeline names as keys, this will return the pipeline if it exists, and None if it does not
  def get_ingest_pipeline(self, ingest_pipeline_name):
    endpoint = '_ingest/pipeline'
    pipelines = self.send_api_request(endpoint, 'GET')
    return pipelines.get(ingest_pipeline_name)
