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

module: elastic_agentpolicy

author: Ian Scott

short_description: Create or Delete Agent Policy by Name or ID from Elastic Deployment

description: 
  - Create or Delete Agent Policy by Name or ID from Elastic Deployment

requirements:
  - python3

options:
      host: ECE Host or Deployment Host
      port: ECE Port or Deployment Port
      username: ECE Username or Deployment Username
      password: ECE Password or Deployment Password
      deployment_info: (when using ECE host:port and credentials)
        deployment_id: ECE Deployment ID
        deployment_name: ECE Deployment Name
        resource_type: kibana
        ref_id: REF ID for kibana cluster, most likely main-kibana
        version: Deployment Kibana Version
      agent_policy_name: Name of Agent Policy
      agent_policy_id: ID of Agent Policy
      monitoring: Monitoring Attributes

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
                
def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', required=True),
        agent_policy_desc=dict(type='str', default='None'),
        state=dict(type='str', default='present'),
        monitoring=dict(type='list', default=[]),
        deployment_info=dict(type='dict', default=None)
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')])
    
    kibana = Kibana(module)
    state = module.params.get('state')
    agent_policy_name = module.params.get('agent_policy_name')
    agent_policy_desc = module.params.get('agent_policy_desc')
    agent_policy_id = module.params.get('agent_policy_id')
    monitoring = module.params.get('monitoring')
    
    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True
    
    if state == "present":
      agent_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
      if agent_policy_object:
        results['agent_policy_status'] = "Agent Policy already exists"
        results['changed'] = False
      else:
        agent_policy_object = kibana.create_agent_policy(agent_policy_id, agent_policy_name, agent_policy_desc, namespace, monitoring)
        results['agent_policy_status'] = "Agent Policy created"
      results['agent_policy_object'] = agent_policy_object
    elif state == "absent":
      agent_policy_object = kibana.delete_agent_policy(None, agent_policy_name)
      results['agent_policy_object'] = agent_policy_object
      if agent_policy_object:
        results['agent_policy_status'] = "Agent Policy deleted"
      else:
        results['agent_policy_status'] = "Agent Policy not found"
    else:
      results['agent_policy_status'] = "A valid state was not passed"
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()