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
        dashboard_name=dict(type='str')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True
                            #,mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            #required_one_of=[('agent_policy_name', 'agent_policy_id')]
                            )
    
    kibana = Kibana(module)
    results['changed'] = False
    dashboard_name = module.params.get('dashboard_name')

    if module.params.get('dashboard_name'):
      dashboard_object = kibana.get_saved_object("dashboard", dashboard_name)
      
    if dashboard_object:
      results['dashboard_status'] = "Dashboard Found"
      results['dashboard_object'] = dashboard_object
    else:
      results['dashboard_status'] = "No Dashboard was returned, check your Dashboard Name"
      results['dashboard_object'] = None
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()