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

def main():
  module_args=dict(
    host=dict(type='str'),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
    action_name=dict(type='str'),
    action_type=dict(type='str', choices=['Email', 'Webhook']), #only the listed choices have been implemented
    config=dict(type='dict'),
    deployment_info=dict(type='dict', default=None),
    secrets=dict(type='dict')
  )

  argument_dependencies = [
    ('state', 'present', ('action_name', 'action_type', 'config'))
  ]

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
  kibana = Kibana(module)
  
  state = module.params.get('state')
  action_name = module.params.get('action_name')
  action_type = module.params.get('action_type')
  config = module.params.get('config')
  secrets = module.params.get('secrets')
    
  action_object = kibana.get_alert_connector_by_name(action_name)
  action_type_id_object = kibana.get_alert_connector_type_by_name(action_type)['id']
  if state =='present':
    if action_object:
      results['msg'] = f'action named {action_name} exists'
      results['action'] = action_object
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'action named {action_name} will be created'
    if not module.check_mode:
      format_config = kibana.format_action_config(action_type, config)
      format_secrets = kibana.format_action_secrets(action_type, secrets)
      results['action'] = kibana.create_action(action_type_id_object, action_name, format_config, format_secrets)
      results['msg'] = f'action named {action_name} created'
    module.exit_json(**results)
  if state == 'absent':
    if not action_object:
      results['msg'] = f'action named {action_name} does not exist'
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'action named {action_name} will be deleted'
    if not module.check_mode:
      kibana.delete_action()
    module.exit_json(**results)

if __name__ == '__main__':
  main()