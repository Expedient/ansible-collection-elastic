#!/usr/bin/python
# Copyright 2021 Expedient
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.module_utils.basic import AnsibleModule

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

import json

results = {}    
    
def main():

    module_args=dict(
        host=dict(type='str',default='elastic-admin.expedient.cloud'),
        port=dict(type='int', default=12443),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_name=dict(type='str')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    deployment_name = module.params.get('deployment_name')
    
    ElasticDeployments = ECE(module)
    
    if deployment_name:
      deployment_kibana_info = ElasticDeployments.get_deployment_kibana_info(deployment_name)
      deployment_object = ElasticDeployments.get_deployment_info(deployment_name)
      if not deployment_kibana_info:
        results['deployment_kibana_endpoint'] = None
        results['deployment_kibana_url'] = None
        results['deployment_kibana_object'] = None
        results['deployment_kibana_info'] = "No deployment kibana was returned, check your deployment name"
      else:
        results['deployment_kibana_endpoint'] = deployment_kibana_info['info']['metadata'].get('aliased_endpoint') or deployment_kibana_info['info']['metadata']['endpoint']
        results['deployment_kibana_url'] = deployment_kibana_info['info']['metadata'].get('aliased_endpoint')
        results['deployment_kibana_object'] = deployment_object
        results['deployment_kibana_info'] = "Deployment kibana was returned sucessfully"
    else:
      deployment_objects = ElasticDeployments.get_deployment_info()
      if deployment_objects:
        results['deployment_objects'] = deployment_objects
      else:
        results['deployment_kibana_info'] = "No deployments were returned, check your deployment name"
      
    #results['deployment_kibana_info'] = deployment_kibana_info


      
      #try:
      #  results['deployment_kibana_endpoint'] = deployment_kibana_info['info']['metadata']['aliased_endpoint']
      #  results['deployment_kibana_url'] = deployment_kibana_info['info']['metadata']['aliased_url']
      #except:
      #  results['deployment_kibana_endpoint'] = deployment_kibana_info['info']['metadata']['endpoint']
      #  results['deployment_kibana_service_url'] = deployment_kibana_info['info']['metadata']['service_url']
      #  results['deployment_kibana_url'] = deployment_kibana_info['info']['metadata']['aliased_url']   
      
    results['changed'] = False
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
