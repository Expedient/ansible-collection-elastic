# Copyright 2021 mike.garuccio
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

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
import time
import requests
from yaml import load, dump
from urllib.error import HTTPError
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ECE_API_Proxy(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.deployment_info = module.params.get('deployment_info')
    self.deployment_id = self.deployment_info['deployment_id']
    self.resource_type = self.deployment_info['resource_type']
    self.ref_id = self.deployment_info['ref_id']
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.ece_auth = ECE(module)


  def send_api_request(self, endpoint, method, data=None, headers={}, timeout=600, space_id='default', no_kbnver=False, version=None):
    
    if endpoint.startswith('_'):
      url = f'https://{self.host}:{self.port}/api/v1/deployments/{self.deployment_id}/{self.resource_type}/{self.ref_id}/proxy/{endpoint}'
    else:
      url = f'https://{self.host}:{self.port}/api/v1/deployments/{self.deployment_id}/{self.resource_type}/{self.ref_id}/proxy/s/{space_id}/api/{endpoint}'
      
    headers = {'Authorization': f'Bearer {self.ece_auth.token}'}
    payload = None
    headers['Content-Type'] = 'application/json'
    headers['X-Management-Request'] = 'True'
    
    if no_kbnver == False and version != None:
      headers['kbn-version'] = version
      
    if data:
      payload = dumps(data)
    response = open_url(
      url, 
      data=payload, 
      headers=headers, 
      method=method, 
      validate_certs=self.validate_certs,
      timeout=timeout
      )
    if response.reason != 'No Content':
      content = loads(response.read())
    else:
      content = ''
    return content

  def send_file_api_request(self, endpoint, method, data=None, headers={}, file=None, timeout=600, space_id = "default", no_kbnver=False, version=None, *args, **kwargs):

    url = f'https://{self.host}:{self.port}/api/v1/deployments/{self.deployment_id}/{self.resource_type}/{self.ref_id}/proxy/s/{space_id}/api/{endpoint}'
    
    response = None
    headers = {}
    headers['Authorization'] =  f'Bearer {self.ece_auth.token}'
    headers['X-Management-Request'] = 'True'
    #headers['Content-Type'] = 'application/json'
      
    if no_kbnver == False and version != None:
      headers['kbn-version'] = version

    if method == "POST":
      try:
        response = requests.post(
          url, 
          files={'file': open(file,'rb')}, 
          headers=headers,
          timeout=timeout
        )
      except HTTPError as e:
        raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.content.decode())

  def get_cluster_status(self):
    endpoint = 'status'
    return self.send_api_request(endpoint, 'GET')

  def get_cluster_version(self):
    status = self.get_cluster_status()
    return status['version']['number']  