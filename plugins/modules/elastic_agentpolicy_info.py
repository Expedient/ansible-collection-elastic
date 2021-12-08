##################################################################
#
#   Script to get Elastic Agent Policy in Deployment
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
import json

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
        agent_policy_name=dict(type='str'),
        agent_policy_id=dict(type='str')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    kibana = Kibana(module)
    results['changed'] = False

    if module.params.get('agent_policy_name'):
      agent_policy_object = kibana.get_agent_policy_byname()
    else:
      agent_policy_object = kibana.get_agent_policy_byid()
      
    results['agent_policy_status'] = "Getting Agent Policy"
    results['agent_policy_object'] = agent_policy_object
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()