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

module: elastic_agentlist_info

author: Ian Scott

short_description: Create Fleet Agent List for Elastic Deployment

description: 
  - Create Fleet Agent List for Elastic Deployment

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
        deployment_info=dict(type='dict', default=None)
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    kibana = Kibana(module)
    results['changed'] = False

    agent_list = kibana.get_agent_list()
    
    results['agent_list_status'] = "Getting Agent List"
    results['agent_list_object'] = agent_list
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()