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

module: elastic_agentpolicy_info

author: Ian Scott

short_description: Get Agent Policy by Name or ID from Elastic Deployment

description: 
  - Get Agent Policy by Name or ID from Elastic Deployment

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
  agent_policy_name: 
    description: Name of Agent Policy
    type: str
  agent_policy_id: 
    description: ID of Agent Policy
    type: str
'''
from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}
                
import json

def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str'),
        agent_policy_id=dict(type='str'),
        deployment_info=dict(type='dict', default=None)
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')])
    
    kibana = Kibana(module)
    results['changed'] = False
    agent_policy_id = module.params.get('agent_policy_id')
    agent_policy_name = module.params.get('agent_policy_name')

    if module.params.get('agent_policy_name'):
      agent_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    else:
      agent_policy_object = kibana.get_agent_policy_byid(agent_policy_id)
      
    if agent_policy_object:
      results['agent_policy_status'] = "Agent Policy Found"
      results['agent_policy_object'] = agent_policy_object
    else:
      results['agent_policy_status'] = "No Agent Policy was returned, check your Agent Policy Name"
      results['agent_policy_object'] = None
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()