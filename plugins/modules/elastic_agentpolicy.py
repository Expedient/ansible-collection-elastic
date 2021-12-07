##################################################################
#
#   Script to create Elastic Agent Policy in Deployment
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule

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
                
def main():

    module_args=dict(    
        host=dict(type='str',Required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', Required=True),
        password=dict(type='str', no_log=True, Required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', Required=True),
        agent_policy_desc=dict(type='str', default='None'),
        state=dict(type='str', default='present')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    AgentPolicies = Kibana(module)
    state = module.params.get('state')

    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True
    
    if state == "present":
      agent_policy_object = AgentPolicies.get_agent_policy_byname()
      if agent_policy_object:
        results['agent_policy_status'] = "Agent Policy already exists"
        results['changed'] = False
      else:
        agent_policy_object = AgentPolicies.create_agent_policy()
        results['agent_policy_status'] = "Creating Agent Policy"
      results['agent_policy_object'] = agent_policy_object
    else:
      results['agent_policy_status'] = "A valid state was not passed"
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()