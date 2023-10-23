#!/usr/bin/python
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

# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: elastic_user

short_description: elastic user management

version_added: '2.9'

author: Mike Garuccio (@mgaruccio)

requirements:
  - python3

description:
  - This module creates or deletes users with elastic
  - Update state not yet implemented

options:
  host:
    description: ECE Host
    type: str
  port:
    description: ECE Port
    type: str
  username:
    description: ECE Username
    type: str
  password:
    description: ECE Password
    type: str
  deployment_info:
    description: Deployment Information
    type: dict
    suboptions:
      deployment_id:
        description: 
        - Deployment ID
        - Required if deployment_name is blank
        type: str
      deployment_name:
        description: 
        - Name of Deployment
        - Required if deployment_id is blank
        type: str
      resource_type:
        description: "Type or Resource, most likely kibana"
        type: str
      ref_id:
        description: "REF ID for kibana cluster, most likely main-kibana"
        type: str
      version:
        description: Deployment Kibana Version
        type: str
  state:
    description:
      - The desired state for the user
    choices:
      - present
      - absent
    default: present
    type: str
  elastic_user:
    description:
      - The name of the user to create or delete
    type: str
    required: True
  elastic_password:
    description:
      - Password for the user
      - Required when creating a new user
    type: str
    required: False
  roles:
    description:
      - list of roles to assign to the user
      - Required when creating a new user
    type: list
    required: False
  full_name:
    description:
      - full name of the user
    type: str
    required: False
  email:
    description:
      - email address to associate with the user
    type: str
    required: False
  metadata:
    description:
      - metadata object to associate with the user
      - can contain any arbitrary key:value pairs
    type: dict
    default: {}
  enabled:
    description:
      - whether to enable the newly created user
    type: bool
    default: True

extends_documentation_fragment:
  - expedient.elastic.elastic_auth_options
'''



try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

from ansible.module_utils.basic import AnsibleModule


class ElasticUser(Elastic):
  def __init__(self, module):
    super().__init__(module)
    self.elastic_username = self.module.params.get('elastic_user')
    self.elastic_password = self.module.params.get('elastic_password')
    self.roles = self.module.params.get('roles')
    self.full_name = self.module.params.get('full_name')
    self.email = self.module.params.get('email')
    self.enabled = self.module.params.get('enabled')
    self.metadata = self.module.params.get('metadata')

    try:
      self.user = self.get_user(self.elastic_username)
    except:
      self.user = None

  def create_user(self):
    endpoint = f'_security/user/{self.elastic_username}'
    data = {
      'password': self.elastic_password,
      'roles': self.roles,
      'full_name': self.full_name,
      'email': self.email,
      'metadata': self.metadata,
      'enabled': self.enabled
    }
    return self.send_api_request(endpoint, data=data, method='POST')

  def delete_user(self):
    endpoint = f'_security/user/{self.elastic_username}'
    return self.send_api_request(endpoint, method='DELETE')



def main():
  module_args=dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    elastic_user=dict(type='str', required=True),
    elastic_password=dict(type='str', required=False, no_log=True),
    roles=dict(type='list', default=[], elements='str'),
    full_name=dict(type='str', required=False),
    email=dict(type='str', required=False),
    metadata=dict(type='dict', default={}),
    enabled=dict(type='bool', default=True),
    deployment_info=dict(type='dict', default=None)
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
  state = module.params.get('state')
  elastic_user = ElasticUser(module)

  if state == 'present':
    if elastic_user.user:
      results['msg'] = f'user {elastic_user.user["username"]} exists'
      module.exit_json(**results)
    results['operation_result'] = elastic_user.create_user()
    module.exit_json(**results)

  if state == 'absent':
    if not elastic_user.user:
      results['msg'] = f'user {module.params.get("elastic_user")} does not exist'
    results['operation_result'] = elastic_user.delete_user()
    module.exit_json(**results)

if __name__ == '__main__':
  main()