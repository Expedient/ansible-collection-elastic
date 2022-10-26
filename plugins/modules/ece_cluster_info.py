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
        deployment_name=dict(type='str'),
        deployment_id=dict(type='str', default=None),
        no_cluster_object=dict(type='bool', default=True)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    deployment_name = module.params.get('deployment_name')
    deployment_id = module.params.get('deployment_id')
    no_cluster_object = module.params.get('no_cluster_object')  
    
    ElasticDeployments = ECE(module)
    deployment_objects = []
    deployment_kibana_endpoint = None
    deployment_kibana_http_port = None
    deployment_kibana_https_port = None
    deployment_kibana_url = None
    
    if deployment_id:
      deployment_objects = [ElasticDeployments.get_deployment_byid(deployment_id)]
    elif deployment_name:
      deployment_objects = [ElasticDeployments.get_deployment_info(deployment_name)]
    else:
      deployment_objects = ElasticDeployments.get_deployment_info()
      deployment_objects = deployment_objects['deployments']
    
    if len(deployment_objects) == 1:
      kibana_info = deployment_objects[0]['resources']['kibana']
      for i in kibana_info:
        if i['ref_id'] == "kibana" or i['ref_id'] == "main-kibana":
          deployment_kibana_endpoint = i['info']['metadata'].get('aliased_endpoint') or i['info']['metadata']['endpoint']
          deployment_kibana_http_port = i['info']['metadata']['ports'].get('http')
          deployment_kibana_https_port = i['info']['metadata']['ports'].get('https')
          deployment_kibana_url = i['info']['metadata'].get('aliased_endpoint')
      results['deployment_kibana_endpoint'] = deployment_kibana_endpoint
      results['deployment_kibana_http_port'] = deployment_kibana_http_port
      results['deployment_kibana_https_port'] = deployment_kibana_https_port
      results['deployment_kibana_url'] = deployment_kibana_url
      if no_cluster_object == False:
        results['deployment_object'] = deployment_objects[0]
      else:
        results['deployment_object'] = "No Cluster Object is True by default to reduce output"
      results['deployment_kibana_info'] = "Deployment was returned sucessfully"
    elif len(deployment_objects) == 0:
      results['deployment_kibana_endpoint'] = None
      results['deployment_kibana_http_port'] = None
      results['deployment_kibana_https_port'] = None
      results['deployment_kibana_url'] = None
      results['deployment_object'] = None
      results['deployment_kibana_info'] = "No deployment was returned, check your deployment name"
    else:
      results['deployment_objects'] = deployment_objects



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
    
     
