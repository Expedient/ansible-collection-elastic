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
  from plugins.modules.elastic_agentpolicy import AgentPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_agentpolicy import AgentPolicy

try:
  from plugins.modules.elastic_rules import Rules
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_rules import Rules

try:
  from plugins.modules.elastic_integration import Integration
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_integration import Integration
  
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

class PkgPolicy(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
        self.agent_policy_name = self.module.params.get('agent_policy_name')
        self.agent_policy_desc = self.module.params.get('agent_policy_desc')
    
    def get_all_pkg_policies(self):
        endpoint  = 'fleet/package_policies'
        pkgpolicy_objects = self.send_api_request(endpoint, 'GET')
        return pkgpolicy_objects
    
    def update_pkg_policy(self,pkgpolicy_id,body):
        endpoint = "fleet/package_policies/" + pkgpolicy_id
        pkg_policy_update = self.send_api_request(endpoint, 'PUT', data=body)
        return pkg_policy_update
    
    def get_pkg_policy(self,pkg_policy_name,agent_policy_id):
      pkg_policy_objects = PkgPolicy.get_all_pkg_policies(self)
      pkg_policy_object = ""
      for pkgPolicy in pkg_policy_objects['items']:
        if pkgPolicy['name'] == pkg_policy_name and pkgPolicy['policy_id'] == agent_policy_id:
          pkg_policy_object = pkgPolicy
          results['pkg_policy_status'] = "Integration Package found, no need to create"
      return(pkg_policy_object)
    
    def create_pkg_policy(self,agent_policy_id, integration_object, pkg_policy_name, pkg_policy_desc, check_mode):
      pkg_policy_object = PkgPolicy.get_pkg_policy(self,pkg_policy_name, agent_policy_id)
      if not pkg_policy_object:
        body = {
          "name": pkg_policy_name,
          "namespace": "default",
          "description": pkg_policy_desc,
          "enabled": True,
          "policy_id": agent_policy_id,
          "output_id": "",
          "inputs": [],
          'package': {
            'name': integration_object['name'],
            'title': integration_object['title'],
            'version': integration_object['version']
          }
        }
        body_JSON = json.dumps(body)
        if check_mode == True: 
          results['pkg_policy_object'] = "Package Policy NOT found or created. Check_mode is set to True. If you would like to create the Integration Package Policy, set check_mode to False"
          return 
        else:
          endpoint  = 'fleet/package_policies'
          pkg_policy_object = self.send_api_request(endpoint, 'POST', data=body)
          return pkg_policy_object
      else:
        return pkg_policy_object

def main():

    module_args=dict(   
        host=dict(type='str',default='id'),
        port=dict(type='int', default=9243),
        username=dict(type='str', default='test1'),
        password=dict(type='str', no_log=True, default='test1'),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', default='Agent Policy'),
        agent_policy_id=dict(type='str'),
        integration_name=dict(type='str', default='Int Name'),
        pkg_policy_name=dict(type='str', default='Int Pkg Name'),
        pkg_policy_desc=dict(type='str', default='Int Pkg Desc'),
        pkg_policy_action=dict(type='str', default='action'),
        pkg_policy_body=dict(type='str', default='body'),
        check_mode=dict(type='bool',default=False)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    pkg_policy = PkgPolicy(module)

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
    
    if module.params.get('pkg_policy_action') == "create":
      pkg_policy_object = pkg_policy.get_pkg_policy(module.params.get('pkg_policy_name'),module.params.get('agent_policy_id'))
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
        results['pkg_policy_object'] = pkg_policy_object
      else:    
        pkg_policy_object = pkg_policy.create_pkg_policy(agent_policy_id, integration_object, module.params.get('pkg_policy_name'), module.params.get('pkg_policy_desc'), module.params.get('check_mode'))
        results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
        results['pkg_policy_object'] = pkg_policy_object
    elif module.params.get('pkg_policy_action') == "get_id_by_name":
      results['changed'] = False
      pkg_policy_object = pkg_policy.get_pkg_policy(module.params.get('pkg_policy_name'),module.params.get('agent_policy_id'))
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found"
        results['pkg_policy_object'] = pkg_policy_object
      else:
        results['pkg_policy_status'] = "Integration Package NOT found"
    else:
      results['pkg_policy_object'] = "A valid action name was not passed"
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
