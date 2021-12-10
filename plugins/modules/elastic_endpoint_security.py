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

class SecurityBaseline(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
        self.integration_pkg_name = module.params.get('integration_pkg_name')
        self.integration_pkg_desc = module.params.get('integration_pkg_desc')
        self.endpoint_security_antivirus = module.params.get('endpoint_security_antivirus')
        self.prebuilt_rules_activate = module.params.get('prebuilt_rules_activate')
        self.agent_policy_name = self.module.params.get('agent_policy_name')
        self.agent_policy_desc = self.module.params.get('agent_policy_desc')
        self.pkg_policy_name = self.module.params.get('pkg_policy_name')
        self.pkg_policy_desc = self.module.params.get('pkg_policy_desc')
        
    def create_securityctrl_baseline_settings(self,pkg_policy_object):
        ################ Checking and creating package policy associated with Integration
        
        try:
          pkg_policy_object['package']
        except:
          pkg_policy_object = pkg_policy_object['item']
          
        if pkg_policy_object['package']['title'] == 'Endpoint Security' and self.module.check_mode == False and self.endpoint_security_antivirus == True:
          i=0
          for input in pkg_policy_object['inputs']:
            if input['type'] == 'endpoint':
                ########## Updating configuration
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['antivirus_registration']['enabled'] = self.endpoint_security_antivirus
                ########## Removing values to reapply the JSON with the above values changed
                pkg_policy_object_id = pkg_policy_object['id'] 
                pkg_policy_object.pop('id')
                pkg_policy_object.pop('revision')
                pkg_policy_object.pop('created_at')
                pkg_policy_object.pop('created_by')
                pkg_policy_object.pop('updated_at')
                pkg_policy_object.pop('updated_by')
                break
            i=+1
          pkg_policy_update = self.update_pkg_policy(pkg_policy_object_id,pkg_policy_object)
          results['pkg_policy_update_status'] = "Updating Endpoint Security Package"
          pkg_policy_info = pkg_policy_update
        
        elif pkg_policy_object['package']['title'] == 'Prebuilt Security Detection Rules' and self.prebuilt_rules_activate == True and self.module.check_mode == False:
              pkg_policy_info = self.activate_rule(50,'Endpoint Security')
        
        elif self.module.check_mode == True:
          results['pkg_policy_update_status'] = "Check mode is set to True, not going to update pkg policy"
        
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
        integration_name=dict(type='str', required=True),
        pkg_policy_name=dict(type='str', required=True),
        pkg_policy_desc=dict(type='str'),
        endpoint_security_antivirus=dict(type='bool', default=True),
        prebuilt_rules_activate=dict(type='bool', default=True),
        state=dict(type='str', default='present')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')])
    
    state = module.params.get('state')
    agent_policy_name = module.params.get('agent_policy_name')
    agent_policy_id = module.params.get('agent_policy_id')
    integration_name = module.params.get('integration_name')
    pkg_policy_name = module.params.get('pkg_policy_name')
    pkg_policy_desc = module.params.get('pkg_policy_desc')
    
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
    
    if module.params.get('integration_name'):
      integration_object = kibana.check_integration(integration_name)
    else:
      results['integration_status'] = "No Integration Name provided to get the integration object"
      results['changed'] = False
      module.exit_json(**results)
    
    if not integration_object:
      results['integration_status'] = 'Integration name is not valid'
      results['changed'] = False
      module.exit_json(**results)
    
    if state == "present":
      pkg_policy_object = kibana.get_pkg_policy(integration_name,agent_policy_id)
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
      else:
        if module.check_mode == False:    
          pkg_policy_object = kibana.create_pkg_policy(pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object)
          results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
          results['changed'] = True
        else:
          results['pkg_policy_status'] = "No Integration Package found, Package Policy not created becans check_mode is set to true"
          results['changed'] = False
              
      if integration_object['title'] == 'Endpoint Security' or integration_object['title'] == 'Prebuilt Security Detection Rules':
        updated_pkg_policy_object = kibana.create_securityctrl_baseline_settings(pkg_policy_object)
        results['updated_pkg_policy_info'] = updated_pkg_policy_object
    
      results['pkg_policy_object'] = pkg_policy_object
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
