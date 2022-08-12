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
from json import loads, dumps

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}

class SecurityBaseline(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
        self.integration_pkg_name = module.params.get('integration_pkg_name')
        self.integration_pkg_desc = module.params.get('integration_pkg_desc')
        self.prebuilt_rules_activate = module.params.get('prebuilt_rules_activate')
        self.agent_policy_name = self.module.params.get('agent_policy_name')
        self.agent_policy_desc = self.module.params.get('agent_policy_desc')
        self.pkg_policy_name = self.module.params.get('pkg_policy_name')
        self.pkg_policy_desc = self.module.params.get('pkg_policy_desc')
        self.integration_settings = self.module.params.get('integration_settings')
    
    def create_securityctrl_baseline_settings(self, pkg_policy_object):
        ################ Checking and creating package policy associated with Integration
        
        if not 'package' in pkg_policy_object:
          pkg_policy_object = pkg_policy_object['item']
        pkg_policy_object_id = pkg_policy_object['id']  
      
        if self.module.check_mode == True:
          results['pkg_policy_update_status'] = "Check mode is set to True, not going to update pkg policy"
          
        elif self.integration_settings:
          #integration_settings_json = loads(self.integration_settings)
          integration_settings_json = self.integration_settings
          results['passed_integration_settings'] = integration_settings_json
          if not 'name' in integration_settings_json:
            integration_settings_json['name'] = pkg_policy_object['name']
          if not 'policy_id' in integration_settings_json:
            integration_settings_json['policy_id'] = pkg_policy_object['policy_id']
          if not 'enabled' in integration_settings_json:
            integration_settings_json['enabled'] = pkg_policy_object['enabled']
          if not 'namespace' in integration_settings_json:
            integration_settings_json['namespace'] = pkg_policy_object['namespace']
          if not 'package' in integration_settings_json:
            integration_settings_json['package'] = pkg_policy_object['package']
          if not 'output_id' in integration_settings_json:
            integration_settings_json['output_id'] = pkg_policy_object['output_id']
          if not 'inputs' in integration_settings_json:
            integration_settings_json['inputs'] = pkg_policy_object['inputs']
          pkg_policy_info = self.update_pkg_policy(pkg_policy_object_id,integration_settings_json)
        
        elif pkg_policy_object['package']['title'] == 'Prebuilt Security Detection Rules' and self.prebuilt_rules_activate == True and self.module.check_mode == False:
              pkg_policy_info = self.activate_security_rule('Endpoint Security')

        else:
          pkg_policy_info = None
        
        return pkg_policy_info

def main():

    module_args=dict(   
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_id=dict(type='str'),
        agent_policy_name=dict(type='str'),
        integration_title=dict(type='str', required=True),
        integration_ver=dict(type='str'),
        integration_name=dict(type='str'),
        pkg_policy_name=dict(type='str', required=True),
        pkg_policy_desc=dict(type='str'),
        namespace=dict(type='str', default='default'),
        prebuilt_rules_activate=dict(type='bool', default=True),
        state=dict(type='str', default='present'),
        integration_settings=dict(type='dict')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')],
                            required_together=[('integration_ver','integration_name')])
    
    state = module.params.get('state')
    agent_policy_name = module.params.get('agent_policy_name')
    agent_policy_id = module.params.get('agent_policy_id')
    integration_title = module.params.get('integration_title')
    integration_ver = module.params.get('integration_ver')
    integration_name = module.params.get('integration_name')
    pkg_policy_name = module.params.get('pkg_policy_name')
    pkg_policy_desc = module.params.get('pkg_policy_desc')
    namespace = module.params.get('namespace')
    integration_settings = module.params.get('integration_settings')

    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True
        
    kibana = SecurityBaseline(module)
    
    if not module.params.get('agent_policy_id'):
      agency_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    else:
      agency_policy_object = kibana.get_agent_policy_byid(agent_policy_id)
    try:
      agent_policy_id = agency_policy_object['id']
      results['agent_policy_status'] = "Agent Policy found."
    except:
      results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
      results['changed'] = False
      module.exit_json(**results)
    
    if module.params.get('integration_title'):
      integration_object = kibana.check_integration(integration_title)
    else:
      results['integration_status'] = "No Integration Title provided to get the integration object"
      results['changed'] = False
      module.exit_json(**results)
    
    if ( integration_name and integration_ver and integration_name) and not integration_object:
      results['integration_status'] = "No integration found, but Integration Name, Version, and Title found"
      integration_object = {
        'name': integration_name,
        'title': integration_title,
        'version': integration_ver
      }
    elif not integration_object and not ( integration_name and integration_ver and integration_name):
      results['integration_status'] = 'Integration Title is not valid and integration name and integration version are not found'
      results['changed'] = False
      module.exit_json(**results)      
    
    if state == "present":
      pkg_policy_object = kibana.get_pkg_policy(integration_title, agent_policy_id)
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
      else:
        if module.check_mode == False:    
          pkg_policy_object = kibana.create_pkg_policy(pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace)
          updated_pkg_policy_object = kibana.create_securityctrl_baseline_settings(pkg_policy_object)
          results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
          results['pkg_policy_object'] = pkg_policy_object
          results['changed'] = True
        else:
          results['pkg_policy_status'] = "No Integration Package found, Package Policy not created becans check_mode is set to true"
          results['pkg_policy_object'] = ""
          results['changed'] = False
        
      results['pkg_policy_object'] = pkg_policy_object
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
