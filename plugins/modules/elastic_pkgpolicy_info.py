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
#from ansible.module_utils.basic import *

import json
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

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
        host=dict(type='str',Required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', Required=True),
        password=dict(type='str', no_log=True, Required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str'),
        agent_policy_id=dict(type='str'),
        integration_name=dict(type='str', Required=True),
        pkg_policy_name=dict(type='str', Required=True)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)

    results['changed'] = False
    kibana = Kibana(module)

    if module.params.get('agent_policy_id'):
      agency_policy_object = kibana.get_agent_policy_byid()
    else:
      agency_policy_object = kibana.get_agent_policy_byname()
    try:
      agent_policy_id = agency_policy_object['id']
      results['agent_policy_status'] = "Agent Policy found."
    except:
      results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
      results['changed'] = False
      module.exit_json(**results)
      
    if module.params.get('integration_name'):
      integration_object = kibana.check_integration(module.params.get('integration_name'))
    else:
      results['integration_status'] = "No Integration Name provided to get the integration object"
      results['changed'] = False
      module.exit_json(**results)
    
    if not integration_object:
      results['integration_status'] = 'Integration name is not a valid'
      results['changed'] = False
      module.exit_json(**results)
    
    pkg_policy_object = kibana.get_pkg_policy(agent_policy_id)
    
    if pkg_policy_object:
      results['pkg_policy_status'] = "Integration Package found"
      results['pkg_policy_object'] = pkg_policy_object
    else:
      results['pkg_policy_status'] = "Integration Package NOT found"
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
