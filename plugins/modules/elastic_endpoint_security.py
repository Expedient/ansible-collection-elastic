##################################################################
#
#   Script to create Elastic Agent Policy in Deployment
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
#from ansible.module_utils.basic import *

import json

try:
  from plugins.modules.elastic_integration import Integration
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_integration import Integration

try:
  from plugins.modules.elastic_agentpolicy import AgentPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_agentpolicy import AgentPolicy
  
try:
  from plugins.modules.elastic_pkgpolicy import PkgPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_pkgpolicy import PkgPolicy

try:
  from plugins.modules.elastic_rules import Rules
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_rules import Rules
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

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
        
    def create_securityctrl_baseline_settings(
        self,
        agent_policy_id, 
        integration_object, 
        integration_pkg_name, 
        integration_pkg_desc, 
        endpoint_security_antivirus, 
        prebuilt_rules_activate, 
        check_mode):
        ###########################################################################################
        #
        # This should be run for the following Integrations:
        #                                      -System
        #                                      -Windows
        #                                      -Linux
        #                                      -Endpoint Security
        #                                      -Prebuilt Security Detection Rules
        #
        # The code will create the policy packages and update them to comply with the baseline
        #
        ###########################################################################################
        
        ################ Checking and creating package policy associated with Integration
      
        pkg_policy_object = PkgPolicy.get_pkg_policy(self, integration_pkg_name,agent_policy_id)
        if pkg_policy_object == "":
          results['pkg_policy_status'] = "Integration Package NOT found, creating package policy"
          pkg_policy_object = PkgPolicy.create_pkg_policy(self, agent_policy_id, integration_object, integration_pkg_name,integration_pkg_desc, check_mode)
        else:
          results['pkg_policy_status'] = "Integration Package found, No package policy created"
          results['changed'] = False
        
        if integration_object['title'] == 'Endpoint Security' and check_mode != True:
          pkgpolicy_objects = PkgPolicy.get_all_pkg_policies(self)
          pkgpolicy_object = ""
          for pkgPolicy in pkgpolicy_objects['items']:
            if pkgPolicy['name'] == integration_pkg_name and pkgPolicy['policy_id'] == agent_policy_id:
              pkgpolicy_object = pkgPolicy
              endPointpkgPolicyId = pkgpolicy_object['id']
              i=0
              for input in pkgpolicy_object['inputs']:
                if input['type'] == 'endpoint':
                  ########## Updating configuration
                  pkgpolicy_object['inputs'][i]['config']['policy']['value']['windows']['antivirus_registration']['enabled'] = endpoint_security_antivirus
                  ########## Removing values to reapply the JSON with the above values changed
                  pkgpolicy_object.pop('id')
                  pkgpolicy_object.pop('revision')
                  pkgpolicy_object.pop('created_at')
                  pkgpolicy_object.pop('created_by')
                  pkgpolicy_object.pop('updated_at')
                  pkgpolicy_object.pop('updated_by')
                  break
                i=+1
          pkgpolicy_object_json = json.dumps(pkgpolicy_object)
          pkg_policy_update = PkgPolicy.update_pkg_policy(self,endPointpkgPolicyId,pkgpolicy_object_json)
          results['pkg_policy_update_status'] = "Updating Endpoint Security Package"
          pkg_policy_object = pkg_policy_update
          
        if integration_object['title'] == 'Prebuilt Security Detection Rules' and prebuilt_rules_activate == True:
            if check_mode == False:
                SecurityRules = Rules.activating_all_rules(self,50)
                results['Activating Rules'] = SecurityRules
            else:
                results['Activating Rules'] = "Check_mode is set to True so rules will not be activated"
        
        return pkg_policy_object

def main():

    module_args=dict(   
        host=dict(type='str',default='id'),
        port=dict(type='int', default=9243),
        username=dict(type='str', default='test1'),
        password=dict(type='str', no_log=True, default='test1'),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', default='Agent Policy'),
        agent_policy_desc=dict(type='str', default='Agent Policy Desc'),
        agent_policy_id=dict(type='str'),
        integration_name=dict(type='str', default='Int Name'),
        integration_pkg_name=dict(type='str', default='Int Pkg Name'),
        integration_pkg_desc=dict(type='str', default='Int Pkg Desc'),
        endpoint_security_antivirus=dict(type='bool', default=False),
        prebuilt_rules_activate=dict(type='bool', default=False),
        check_mode=dict(type='bool',default=False)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    if module.params.get('check_mode') == True:
        results['changed'] = False
    else:
        results['changed'] = True
        
    if not module.params.get('agent_policy_id'):
      ElasticAgentPolicyId = AgentPolicy(module)
      agency_policy_object = ElasticAgentPolicyId.get_agent_policy_id_byname(module.params.get('agent_policy_name'))
      try:
        agent_policy_id = agency_policy_object['id']
        results['agent_policy_status'] = "Agent Policy found."
      except:
        results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
        results['changed'] = False
        module.exit_json(**results)
    else:
      results['agent_policy_status'] = "Agent Policy ID found."
      agent_policy_id = module.params.get('agent_policy_id')
    
    ElasticIntegration = Integration(module)
    if module.params.get('integration_name'):
      integration_object = ElasticIntegration.check_integration(module.params.get('integration_name'))
    else:
      results['integration_status'] = "No Integration Name provided to get the integration object"
      results['changed'] = False
      module.exit_json(**results)
    
    if not integration_object:
      results['integration_status'] = 'Integration name is not a valid'
      results['changed'] = False
      module.exit_json(**results)
            
    ElasticSecurityBaseline = SecurityBaseline(module)
    pkg_policy_object = ElasticSecurityBaseline.create_securityctrl_baseline_settings(
      agent_policy_id, 
      integration_object,
      module.params.get('integration_pkg_name'),
      module.params.get('integration_pkg_desc'),
      module.params.get('endpoint_security_antivirus'),
      module.params.get('prebuilt_rules_activate'),
      module.params.get('check_mode')
    )
    
    results['pkg_policy_object'] = pkg_policy_object
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
