##################################################################
#
#   Script to create Elastic Agent Policy in Deployment
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
import json

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic_integration import Integration
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic_integration import Integration

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic_agentpolicy import AgentPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic_agentpolicy import AgentPolicy
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic_pkgpolicy import PkgPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic_pkgpolicy import PkgPolicy

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic_rules import Rules
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
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
        pkg_policy_action = PkgPolicy(self.module)
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
          pkg_policy_object_json = json.dumps(pkg_policy_object)
          pkg_policy_update = pkg_policy_action.update_pkg_policy(pkg_policy_object_id,pkg_policy_object_json)
          results['pkg_policy_update_status'] = "Updating Endpoint Security Package"
          pkg_policy_info = pkg_policy_update
        
        elif pkg_policy_object['package']['title'] == 'Prebuilt Security Detection Rules' and self.prebuilt_rules_activate == True and self.module.check_mode == False:
              rules_action = Rules(self.module)
              #SecurityRules = rules_action.activating_all_rules(self,50)
              pkg_policy_info = rules_action.activate_rule(50,'Endpoint Security')
        
        elif self.module.check_mode == True:
          results['pkg_policy_update_status'] = "Check mode is set to True, not going to update pkg policy"
        
        return pkg_policy_info

def main():

    module_args=dict(   
        host=dict(type='str',default='id'),
        port=dict(type='int', default=9243),
        username=dict(type='str', default='test1'),
        password=dict(type='str', no_log=True, default='test1'),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_id=dict(type='str'),
        agent_policy_name=dict(type='str'),
        integration_name=dict(type='str', default='Int Name'),
        pkg_policy_name=dict(type='str', default='Int Pkg Name'),
        pkg_policy_desc=dict(type='str', default='Int Pkg Desc'),
        endpoint_security_antivirus=dict(type='bool', default=False),
        prebuilt_rules_activate=dict(type='bool', default=False)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True
        
    agent_policy_action = AgentPolicy(module)
    if not module.params.get('agent_policy_id'):
      agency_policy_object = agent_policy_action.get_agent_policy_id_byname()
    else:
      agency_policy_object = agent_policy_action.get_agent_policy_byid()
    try:
      agent_policy_id = agency_policy_object['id']
      results['agent_policy_status'] = "Agent Policy found."
    except:
      results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
      results['changed'] = False
      module.exit_json(**results)
    
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
    
    pkg_policy_action = "create"
    pkg_policy = PkgPolicy(module)
    if pkg_policy_action == "create":
      pkg_policy_object = pkg_policy.get_pkg_policy(agent_policy_id)
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
        results['pkg_policy_object'] = pkg_policy_object
      else:    
        pkg_policy_object = pkg_policy.create_pkg_policy(agent_policy_id, integration_object)
        results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
        results['pkg_policy_object'] = pkg_policy_object
            
    ElasticSecurityBaseline = SecurityBaseline(module)
    if integration_object['title'] == 'Endpoint Security' or integration_object['title'] == 'Prebuilt Security Detection Rules':
      updated_pkg_policy_object = ElasticSecurityBaseline.create_securityctrl_baseline_settings(pkg_policy_object)
      results['updated_pkg_policy_info'] = updated_pkg_policy_object
    
    results['pkg_policy_object'] = pkg_policy_object
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
