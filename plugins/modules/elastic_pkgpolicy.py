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
  from plugins.modules.elasticCreateAgentPolicy import AgentPolicy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/modules'
  sys.path.append(util_path)
  from elastic_agentpolicy import AgentPolicy
  
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
    
    def activating_rules(self,module):

      ########## Activating all rules
      #### Getting first page of rules
      page_size = 50
      page_number = 1
      endpoint = "detection_engine/rules/_find?page=" + str(page_number) + "&per_page=" + str(page_size)
      rules = self.send_api_request(endpoint, 'GET')
      noOfRules = rules['total']
      allrules = rules['data']
      #### Going through each rule page by page and enabling each rule that isn't enabled.
      results['Updating Rules'] = 'Activating ' + str(noOfRules) + ' Rules.'
      while noOfRules > page_size * (page_number - 1):
          #print("Processing page " + str(page_number))
          for rule in allrules:
              #print("Updating rule " + rule['name'])
              body={
                'enabled': True,
                'id': rule['id']
              }
              body_JSON = json.dumps(body)
              if rule['enabled'] == False:
                endpoint = "detection_engine/rules"
                updateRule = self.send_api_request(endpoint,'PATCH',data=body)
                results['Rule: ' + rule['name']] = 'Activating'
                return("Rule is updated")
          page_number = page_number + 1
          endpoint = "detection_engine/rules/_find?page=" + str(page_number) + "&per_page=" + str(page_size)
          rules = self.send_api_request(endpoint, 'GET')
          allrules = rules['data']
      return("Rules are updated as indicated in results")
    
    def create_pkg_policy(self,agent_policy_id, integration_name, integration_pkg_name, integration_pkg_desc, check_mode):
      
        ################ Checking Integrations to validate the one to be configured is installed
        results['check_mode'] = str(check_mode)
        endpoint  = 'fleet/epm/packages'
        integration_objects = self.send_api_request(endpoint, 'GET')
        integration_object = ""
        for integration in integration_objects['response']:
          if integration['title'] in integration_name:
            integration_object = integration
            if integration['status'] != 'installed':
              results["integration_status"] = 'Installing integration'
              body = {
                "force": True
              }
              body_JSON = json.dumps(body)
              endpoint  = 'fleet/epm/packages/' + integration['name'] + "-" + integration['version']
              integration_install = self.send_api_request(endpoint, 'POST', data=body_JSON)
              results['changed'] = True
              results['integration_install'] = integration_install
          else:
              results['integration_status'] = 'Integration is already installed.'
        if integration_object == "":
          results['integration_status'] = 'Integration does not exist.'
          return()
        # results['integration_object'] = integration_object
        ################ Checking and creating package policy associated with Integration
        
        pkgpolicy_objects = PkgPolicy.get_all_pkg_policies(self)
        pkgPolicy_object = ""
        for pkgPolicy in pkgpolicy_objects['items']:
          if pkgPolicy['name'] == integration_pkg_name and pkgPolicy['policy_id'] == agent_policy_id:
            pkgPolicy_object = pkgPolicy
            results['integration_pkg_status'] = "Integration Package found, no need to create"

        if pkgPolicy_object == "":
          results['integration_pkg_status'] = "Integration Package NOT found, creating package policy"
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
          else:
            endpoint  = 'fleet/package_policies'
            pkgPolicy_object = self.send_api_request(endpoint, 'POST', data=body_JSON)
            results['changed'] = True
        else:
          results['changed'] = False
        results['integration_pkg_object'] = pkgPolicy_object
        
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
          endpoint = "fleet/package_policies/" + endPointpkgPolicyId
          pkg_policy_update = self.send_api_request(endpoint, 'PUT', data=pkgpolicy_object_json)
          results['changed'] = True
          results['pkg_policy_update_object'] = pkg_policy_update
        return ("Package Policy is created as results indicate")
  
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
    
    if module.params.get('integration_name') == 'Prebuilt Security Detection Rules':
      if module.params.get('check_mode') == False:
        ElasticRuleActivate = ElasticPkgPolicy.activating_rules(module)
        results['Activating Rules'] = ElasticRuleActivate
      else:
        results['Activating Rules'] = "Check_mode is set to True so rules will not be activeated"
        
    #print(results)
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
