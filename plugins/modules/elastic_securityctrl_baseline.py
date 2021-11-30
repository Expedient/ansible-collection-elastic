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
        
    def create_securityctrl_baseline_settings(self,agent_policy_id, integration_name, integration_pkg_name, integration_pkg_desc, check_mode):
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
        
        ################ Checking Integrations to validate the one to be configured is installed
        ElasticIntegration = Integration(self)
        integration_object = ElasticIntegration.check_integration(integration_name, check_mode)
        ################ Checking and creating package policy associated with Integration
      
        integration_pkg_object = PkgPolicy.get_pkg_policy(self, integration_pkg_name,agent_policy_id)
        if integration_pkg_object == "":
          results['integration_pkg_status'] = "Integration Package NOT found, creating package policy"
          pkgPolicy_object = PkgPolicy.create_pkg_policy_object(self, agent_policy_id, integration_object, integration_pkg_name,integration_pkg_desc, check_mode)
          results['integration_pkg_object'] = pkgPolicy_object
        else:
          results['changed'] = False
          results['integration_pkg_status'] = "Integration Package found, No package policy created"
        
        if integration_name == 'Endpoint Security' and check_mode != True:
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
                  pkgpolicy_object['inputs'][i]['config']['policy']['value']['windows']['antivirus_registration']['enabled'] = True
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
          results['changed'] = True
          results['pkg_policy_update_object'] = pkg_policy_update
          
        if integration_name == 'Prebuilt Security Detection Rules':
          if check_mode == False:
            SecurityRules = Rules.activating_all_rules(self,50)
            results['Activating Rules'] = SecurityRules
          else:
            results['Activating Rules'] = "Check_mode is set to True so rules will not be activeated"
  
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
        check_mode=dict(type='bool',default=False)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    if not module.params.get('agent_policy_id'):
      ElasticAgentPolicyId = AgentPolicy(module)
      agency_policy_object = ElasticAgentPolicyId.get_agent_policy_id_byname(module.params.get('agent_policy_name'))
      if not agency_policy_object:
          agent_policy_inst = AgentPolicy(module)
          if module.params.get('check_mode') == False:
            results['changed'] = True
            agency_policy_object = agent_policy_inst.create_agent_policy(module.params.get('agent_policy_name'),module.params.get('agent_policy_desc'), module.params.get('check_mode'))
          else:
            results['changed'] = False
            return("Cannot proceed with check_mode set to " + module.params.get('check_mode'))
      agent_policy_id = agency_policy_object['id']
    else:
      results['changed'] = False
      agent_policy_id = module.params.get('agent_policy_id')
    results['agent policy object'] = agency_policy_object
    ElasticSecurityBaseline = SecurityBaseline(module)
    PkgPolicyInfo = ElasticSecurityBaseline.create_securityctrl_baseline_settings(
      agent_policy_id, 
      module.params.get('integration_name'),
      module.params.get('integration_pkg_name'),
      module.params.get('integration_pkg_desc'),
      module.params.get('check_mode')
    )
    #ElasticIntegration = Integration(module)
    #integration_object = ElasticIntegration.check_integration(module.params.get('integration_name'))
    #if not integration_object:
    #    return(module.params.get('integration_name') + ": NOT a valid integration")
    #results['integration object'] = integration_object
    
    #ElasticPkgPolicy = PkgPolicy(module)
    #PkgPolicyInfo = ElasticPkgPolicy.create_pkg_policy(
    #  agent_policy_id,
    #  integration_object,
    #  module.params.get('integration_pkg_name'),
    #  module.params.get('integration_pkg_desc'),
    #  module.params.get('check_mode')
    #)
    results['pkg_policy_object'] = PkgPolicyInfo
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
