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
        deployment_info=dict(type='dict', default=None),
        verify_ssl_cert=dict(type='bool', default=True)
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    kibana = Kibana(module)
    results['changed'] = False

    fleet_agent_list = kibana.get_agent_list()
    pkg_policy_list = kibana.get_all_pkg_policies()
    agent_policy_list = kibana.get_all_agent_policys()
    
    #results['pkg_policy_list'] = pkg_policy_list
    #results['agent_policy_list'] = agent_policy_list
    #results['agent_list'] = agent_list
    i=0
    for agent_policy in agent_policy_list['items']:
      if 'package_policy_info' not in agent_policy:
        agent_policy_list['items'][i]['package_policy_info'] = []
      if 'package_policies' in agent_policy:
        for pkg_policy_per_agent_policy in agent_policy['package_policies']:
          for pkg_policy in pkg_policy_list['items']:
            if pkg_policy_per_agent_policy == pkg_policy['id']:
              package_policy_info = {
                'pkg_policy_name': pkg_policy['name'],
                'integration_name': pkg_policy['package']['name'],
                #'integration_title': pkg_policy['package']['title'],
                #'integration_version': pkg_policy['package']['version'],              
              }
              agent_policy_list['items'][i]['package_policy_info'].append(package_policy_info)
      
      i=i+1
    agent_list = []
    for fleet_agent in fleet_agent_list['list']:
      for agent_policy in agent_policy_list['items']:
        if fleet_agent['policy_id'] == agent_policy['id']:
          if 'agent' not in fleet_agent:
            fleet_agent['agent'] = {}
            fleet_agent['agent']['version'] = "N/A"
          agent_entry = {
            'agent_name': fleet_agent['local_metadata']['host']['name'],
            'host_name':fleet_agent['local_metadata']['host']['hostname'],
            'agent_active': fleet_agent['active'],
            'agent_status': fleet_agent['status'],
            'agent_version': fleet_agent['agent']['version'],
            'agent_policy': agent_policy['name'],
            'pkg_policy_info': agent_policy['package_policy_info']
          }
          agent_list.append(agent_entry)
          results['agent_list'] = agent_list
      
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()