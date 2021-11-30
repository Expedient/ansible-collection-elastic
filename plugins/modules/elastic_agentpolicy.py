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

class AgentPolicy(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
        #self.agent_policy_name = self.module.params.get('agent_policy_name')
        #self.agent_policy_desc = self.module.params.get('agent_policy_desc')
        #self.check_mode = self.module.params.get('check_mode')
                
    def create_agent_policy(self, agent_policy_name, agent_policy_desc, check_mode):
      endpoint  = 'fleet/agent_policies'
      agent_policy_object = ""
      agent_policy_objects = self.send_api_request(endpoint, 'GET')
      results['check_mode'] = 'Check_mode is ' + str(check_mode)
      for agent_policy in agent_policy_objects['items']:
          if agent_policy['name'] == agent_policy_name:
              agent_policy_object = agent_policy
              results['changed'] = False
              results['agent_policy_status'] = 'Existing'
              results['agent_policy_object'] = agent_policy
              continue
              
      if not agent_policy_object:
        body = {
            "name": agent_policy_name,
            "namespace": "default",
            "description": agent_policy_desc,
            "monitoring_enabled": []
        }
        body_JSON = json.dumps(body)
        
        if check_mode == True:
          results['changed'] = False
        else:
          results['changed'] = True
          agent_policy_object = self.send_api_request(endpoint, 'POST', data=body_JSON)
          agent_policy_object = agent_policy_object['item']
          results['agent_policy_status'] = 'Created'
        results['msg'] = body_JSON
        results['agent_policy_object'] = agent_policy_object
      return(results)

    def get_agent_policy_id_byname(self, agent_policy_name):
      endpoint  = 'fleet/agent_policies'
      agent_policy_object = ""
      agent_policy_objects = self.send_api_request(endpoint, 'GET')
      for agent_policy in agent_policy_objects['items']:
          if agent_policy['name'] == agent_policy_name:
              agent_policy_object = agent_policy
              results['agent_policy_status'] = 'Exists'
              continue
      if not agent_policy_object:
        results['agent_policy_status'] = 'Does not exist'
      results['agent_policy_object'] = agent_policy_object
      results['changed'] = False
      return(results)
                
def main():

    module_args=dict(    
        host=dict(type='str',default='id'),
        port=dict(type='int', default=9243),
        username=dict(type='str', default='test1'),
        password=dict(type='str', no_log=True, default='test'),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', default='Ansible-Elastic-API-Testing'),
        agent_policy_desc=dict(type='str', default='None'),
        check_mode=dict(type='bool',default=False)
    )
    
    #args = json.dumps(module_args)
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    #module.params['host'] = module.params['host'] + ".elastic.expedient.cloud"
    AgentPolicies = AgentPolicy(module)
    AgentPolicies.create_agent_policy(module.params.get('agent_policy_name'), module.params.get('agent_policy_desc'), module.params.get('check_mode'))
    module.exit_json(**results)

if __name__ == "__main__":
    main()