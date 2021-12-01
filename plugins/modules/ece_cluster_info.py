##################################################################
#
#   Script to get Elastic Deployment ID and object from Elastic Admin
#
#   Version 1.0 - 11/17/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import AnsibleModule
#from ansible.module_utils.basic import *

import json

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


class Deployments(ECE):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
        self.deployment_name = self.module.params.get('deployment_name')
        self.deployment_action = self.module.params.get('deployment_action')
        self.deployment_body = self.module.params.get('deployment_body')
        self.check_mode = self.module.params.get('check_mode')
        
    def get_deployment_id(self,deployment_name):

        endpoint  = 'deployments'
        deployment_objects = self.send_api_request(endpoint, 'GET')
        deployment_list = []
        deployment_object = ""
        for deployment in deployment_objects['deployments']:
          deployment_list.append(str(deployment['name']))
          if deployment['name'] == deployment_name:
            deployment_object = deployment
            for resource in deployment['resources']:
              if resource['ref_id'] == 'main-kibana':
                deployment_id = resource['id']
                break

        results['deployment_object'] = deployment_object
        try:
          results['deployment_id'] = deployment_id
        except:
          results['deployment_status'] = "A valid deployment name was not given"
        return results
    
def main():

    module_args=dict(
        host=dict(type='str',default='elastic-admin.expedient.cloud'),
        port=dict(type='int', default=12443),
        username=dict(type='str', default='test1'),
        password=dict(type='str', no_log=True, default='test1'),
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_name=dict(type='str', default='Expedient-prodops-testing'),
        deployment_action=dict(type='str', default='action'),
        deployment_body=dict(type='str', default='body'),
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
    
    ElasticDeployments = Deployments(module)
    
    if module.params.get('deployment_action') == "get_deployment_id":
      ElasticDeployments.get_deployment_id(module.params.get('deployment_name'))
    else:
      results['deployment_status'] = "A valid action name was not passed"
   
    results['changed'] = False
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     