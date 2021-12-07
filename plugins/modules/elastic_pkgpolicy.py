##################################################################
#
#   Script to create Elastic Agent Policy in Deployment
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
#from ansible.module_utils.basic import *
  
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

def main():

    module_args=dict(   
        host=dict(type='str',Required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', Required=True),
        password=dict(type='str', no_log=True, Required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_name=dict(type='str', default='Agent Policy'),
        agent_policy_id=dict(type='str'),
        integration_name=dict(type='str', Required=True),
        pkg_policy_name=dict(type='str', Required=True),
        pkg_policy_desc=dict(type='str'),
        pkg_policy_body=dict(type='str', default='body'),
        state=dict(type='str', default='present')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    pkg_policy = Kibana(module)
    state = module.params.get('state')
    
    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True

    agent_policy_action = Kibana(module)
    if not module.params.get('agent_policy_id'):
      agency_policy_object = agent_policy_action.get_agent_policy_byid(agent_policy_action.get_agent_policy_id_byname())
    else:
      agency_policy_object = agent_policy_action.get_agent_policy_byid(module.params.get('agent_policy_id'))
    try:
      agent_policy_id = agency_policy_object['id']
      results['agent_policy_status'] = "Agent Policy found."
    except:
      results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
      results['changed'] = False
      module.exit_json(**results)
      
    ElasticIntegration = Kibana(module)
    
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
    
    if state == "present":
      pkg_policy_object = pkg_policy.get_pkg_policy(agent_policy_id)
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
        results['pkg_policy_object'] = pkg_policy_object
      else:    
        pkg_policy_object = pkg_policy.create_pkg_policy(agent_policy_id, integration_object)
        results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
        results['pkg_policy_object'] = pkg_policy_object
    else:
      results['pkg_policy_object'] = "A valid state was not passed"
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
