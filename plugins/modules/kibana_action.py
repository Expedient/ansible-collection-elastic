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

from ansible.module_utils.six import assertRaisesRegex
#from plugins.modules.ece_cluster import DOCUMENTATION


ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

from ansible.module_utils.basic import AnsibleModule


class KibanaAction(Kibana):
  def __init__(self, module):
    super().__init__(module)
    self.module = module
    self.state = self.module.params.get('state')
    self.action_name = self.module.params.get('action_name')
    self.action_type = self.module.params.get('action_type')
    self.action_type_id = self.get_alert_connector_type_by_name(self.action_type)['id']
    self.config = self.module.params.get('config')
    self.secrets = self.module.params.get('secrets')
    self.action = self.get_alert_connector_by_name(self.action_name)

  def format_config(self):
    if self.action_type == 'Webhook':
      return {
        'method': self.config['method'],
        'hasAuth': self.config['auth'],
        'url': self.config['url'],
        'headers': self.config['headers']
      }
    if self.action_type == 'Email':
      return {
        'from': self.config['sender'],
        'hasAuth': self.config['auth'],
        'host': self.config['host'],
        'port': self.config['port']
      }
    
  def format_secrets(self):
    secrets = {}
    if self.action_type == 'webhook' and 'user' in self.secrets:
      secrets['user'] = self.secrets['user']
      secrets['password'] = self.secrets['password']
    return secrets

  def create_action(self):
    endpoint = 'actions/connector'
    data = {
      'connector_type_id': self.action_type_id,
      'name': self.action_name,
      'config': self.format_config(),
      'secrets': self.format_secrets()
    }
    return self.send_api_request(endpoint, 'POST', data=data)

  def delete_action(self):
    endpoint = f'actions/connector/{self.action["id"]}'
    return self.send_api_request(endpoint, 'DELETE')

def main():
  module_args=dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=9243),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
    action_name=dict(type='str'),
    action_type=dict(type='str', choices=['Email', 'Webhook']), #only the listed choices have been implemented
    config=dict(type='dict'),
    secrets=dict(type='dict')
  )

  argument_dependencies = [
    ('state', 'present', ('action_name', 'action_type', 'config'))
  ]

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
  state = module.params.get('state')

  kibana_action = KibanaAction(module)

  if state =='present':
    if kibana_action.action:
      results['msg'] = f'action named {kibana_action.action_name} exists'
      results['action'] = kibana_action.action
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'action named {kibana_action.action_name} will be created'
    if not module.check_mode:
      results['action'] = kibana_action.create_action()
      results['msg'] = f'action named {kibana_action.action_name} created'
    module.exit_json(**results)
  if state == 'absent':
    if not kibana_action.action:
      results['msg'] = f'action named {kibana_action.action_name} does not exist'
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'action named {kibana_action.action_name} will be deleted'
    if not module.check_mode:
      kibana_action.delete_action()
    module.exit_json(**results)



if __name__ == '__main__':
  main()