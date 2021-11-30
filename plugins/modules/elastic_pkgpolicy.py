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
    
    def get_pkg_policy(self,integration_pkg_name,agent_policy_id):
      pkg_policy_objects = PkgPolicy.get_all_pkg_policies(self)
      pkg_policy_object = ""
      for pkgPolicy in pkg_policy_objects['items']:
        if pkgPolicy['name'] == integration_pkg_name and pkgPolicy['policy_id'] == agent_policy_id:
          pkg_policy_object = pkgPolicy
          results['integration_pkg_status'] = "Integration Package found, no need to create"
      return(pkg_policy_object)
    
    def create_pkg_policy(self,agent_policy_id, integration_object, integration_pkg_name, integration_pkg_desc, check_mode):
      body = {
        "name": integration_pkg_name,
        "namespace": "default",
        "description": integration_pkg_desc,
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
        results['changed'] = False
        results['msg'] = body_JSON
        results['pkgPolicy_object'] = "Package Policy NOT found or created. Check_mode is set to True. If you would like to create the Integration Package Policy, set check_mode to False"
        return
      else:
        endpoint  = 'fleet/package_policies'
        pkgPolicy_object = self.send_api_request(endpoint, 'POST', data=body)
        results['changed'] = True
        return pkgPolicy_object

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
      AgentPolicyObject = ElasticAgentPolicyId.get_agent_policy_id_byname(module.params.get('agent_policy_name'))
      agent_policy_id = AgentPolicyObject['agent_policy_object']['id']
    else:
      agent_policy_id = module.params.get('agent_policy_id')
      
    ElasticPkgPolicy = PkgPolicy(module)
    PkgPolicyInfo = ElasticPkgPolicy.create_pkg_policy(
      agent_policy_id,
      module.params.get('integration_name'),
      module.params.get('integration_pkg_name'),
      module.params.get('integration_pkg_desc'),
      module.params.get('check_mode')
    )
    results['pkg_policy_object'] = PkgPolicyInfo
  
    #print(results)
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
