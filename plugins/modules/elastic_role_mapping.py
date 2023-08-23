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

DOCUMENTATION='''

module: elastic_role_mapping

author: Ian Scott

short_description: Show info on a Role Mapping

description: 
  - Show info on a Role Mapping

requirements:
  - python3

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
        required: False
        description: ECE Deployment ID
        type: str
      deployment_name:
        required: False
        description: ECE Deployment Name
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
  role_mapping_name: 
    description: Role Mapping name (Required)
    type: str
  enabled: 
    description: Enable Mapping, True/False
    type: boolean
  roles:
    description: List of assinged Roles
    type: list
  rules:
    description: Deployment Information
    type: dict
    suboptions:
      realm.name:
        description: Realm Name
        type: str
      groups:
        description: User Group
        type: str
  
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


class ElasticRoleMapping(Elastic):
  def __init__(self, module):
    super().__init__(module)
    self.role_mapping_name = self.module.params.get('name')
    self.enabled = self.module.params.get('enabled')
    self.roles = self.module.params.get('roles')
    self.rules = self.module.params.get('rules')
    try:
      self.role_mapping = self.get_role_mapping(self.role_mapping_name)
    except:
      self.role_mapping = None

  def create_role_mapping(self):
    endpoint = f'_security/role_mapping/{self.role_mapping_name}'
    data = {
      'enabled': self.enabled,
      'roles': self.roles,
      'rules': self.rules,
      'metadata': self.metadata
    }
    self.send_api_request(endpoint, data=data, method='POST')



def main():
  module_args=dict(
    host=dict(type='str'),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    name=dict(type='str', required=True),
    enabled=dict(type='bool', default=True),
    roles=dict(type='list', required=True),
    rules=dict(type='dict', required=True),
    metadata=dict(type='dict', default={}),
    deployment_info=dict(type='dict')
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
  state = module.params.get('state')
  role_mapping = ElasticRoleMapping(module)

  if state == 'present':
    if role_mapping.role_mapping:
      results['msg'] = f'role mapping {role_mapping.role_mapping_name} exists'
      module.exit_json(**results)
    


if __name__ == '__main__':
  main()