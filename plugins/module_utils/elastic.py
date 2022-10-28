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

#from operator import contains
from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
from urllib.error import HTTPError
#import urllib.parse
#import requests
#import tempfile
#import os

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece_apiproxy import ECE_API_Proxy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece_apiproxy import ECE_API_Proxy

class Elastic(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.deployment_info = module.params.get('deployment_info')
    if self.deployment_info:
      self.ece_api_proxy = ECE_API_Proxy(module)
      
  def send_api_request(self, endpoint, method, data = None, headers = {}, timeout = 120, *args, **kwargs):
    
    if self.deployment_info:
      result = self.ece_api_proxy.send_api_request(endpoint, method, data, headers, timeout)
    else:
      result = self.send_elastic_api_request(endpoint, method, data, headers, timeout)
    return result

  def send_elastic_api_request(self, endpoint, method, data=None, headers={}, timeout=120, *args, **kwargs):
    
    url = f'https://{self.host}:{self.port}/{endpoint}'

    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    try:
      response = open_url(url, data=payload, method=method, validate_certs=self.validate_certs, headers=headers,
                          force_basic_auth=True, url_username=self.username, url_password=self.password, timeout=timeout)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    if response.msg == 'No Content' and str(response.status).startswith('2'):
      return
    else:
      response_output = response.read()
      response_str = response_output.decode()
      response_return = str(response_str).split('\n')
      response_list = []
      for i in response_return:
        return_load = loads(i)
        response_list.append(return_load)
      if len(response_list) > 1:
        return response_list
      else:
        return response_list[0]

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

  def create_role_mapping(self, role_mapping_name, assigned_roles, role_mapping_rules, enable_mapping=True, metadata={}, *args, **kwargs):
    endpoint = f'_security/role_mapping/{role_mapping_name}'
    data = {
      'enabled': enable_mapping,
      'roles': assigned_roles,
      'rules': role_mapping_rules
    }
    role_mapping_object = self.send_api_request(endpoint, data=data, method='POST')
    return role_mapping_object