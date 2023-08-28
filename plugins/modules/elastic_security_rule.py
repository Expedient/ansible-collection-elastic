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
DOCUMENTATION='''

module: elastic_savedobject

author: Ian Scott

short_description: Get Elastic Saved Object List or Create Saved Object.

description: 
  - Get Elastic Saved Object List or Create Saved Object.

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
  connector_name:
    description: The name of the connector
    type: str
  rule_name:
    description: The name of the Rule
    type: str
  action_body:
    description: Action Body
    type: str
  action_group:
    description: Action Group
    type: str
  replace_or_append:
    description: Replace or Append Action
    type: str


'''
from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
import json

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}
                
def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        connector_name=dict(type='str', required=True),
        rule_name=dict(type='str', required=True),
        action_body=dict(type='str'),
        action_group=dict(type='str'),
        replace_or_append=dict(type='str'),
        state=dict(type='str', default='present'),
        #existing_actions=dict(type='str'),
        deployment_info=dict(type='dict', default=None)
    ) 
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True,
                            required_together=[['action_body', 'action_group', 'replace_or_append']])
    kibana = Kibana(module)
    results['changed'] = True
    connector_name = module.params.get('connector_name')
    rule_name = module.params.get('rule_name')
    action_body = module.params.get('action_body')
    action_group = module.params.get('action_group')
    replace_or_append = module.params.get('replace_or_append')
    state = module.params.get('state')    

    if state =='present':
      connector_exists = kibana.get_alert_connector_by_name(connector_name)
      if not connector_exists:
        results['msg'] = f'action named {connector_name} does not exist'
        results['connector_status'] = "Connector does not exist, exiting"
        results['connector_object'] = connector_exists
        module.exit_json(**results)
      else:
        results['msg'] = f'action named {connector_name} exists'
        results['connector_status'] = "Connector exists by that name"
        results['connector_object'] = connector_exists
      
      target_rule = kibana.get_security_rule_byname(rule_name)

      if not target_rule:
        results['msg'] = f'rule named {rule_name} does not exist'
        results['rule_status'] = "Rule does not exist, exiting"
        results['rule_object'] = target_rule
        module.exit_json(**results)
      else:
        results['msg'] = f'rule named {rule_name} exists'
        results['rule_status'] = "Rule exists by that name"
        results['rule_object'] = target_rule
      
      existing_actions = target_rule['actions']
      rule_action_object = kibana.enable_security_rule_action(
        target_rule['id'],
        connector_exists['id'],
        connector_exists['connector_type_id'], 
        action_body, 
        replace_or_append, 
        existing_actions, 
        action_group
      )
      results['rule_action_status'] = "Created Rule Action Connector"
      results['rule_action_object'] = rule_action_object
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()