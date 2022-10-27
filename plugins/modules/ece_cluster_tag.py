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
from importlib_metadata import metadata

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
        no_cluster_object=dict(type='bool', default=True),
        tag_label=dict(type='str'),
        tag_value=dict(type='str')
        
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    deployment_name = module.params.get('deployment_name')
    deployment_id = module.params.get('deployment_id')
    no_cluster_object = module.params.get('no_cluster_object')  
    tag_label = module.params.get('tag_label') 
    tag_value = module.params.get('tag_value')
    results = { 'changed': True }
        
    ElasticDeployments = ECE(module)
    
    if deployment_id:
      deployment_object = [ElasticDeployments.get_deployment_byid(deployment_id)]
    elif deployment_name:
      deployment_object = [ElasticDeployments.get_deployment_info(deployment_name)]
    
    if deployment_object:
      tag_body = {
        "key": tag_label,
        "value": tag_value
      }
      if 'tags' not in deployment_object[0]['metadata']:
        deployment_object[0]['metadata']['tags'] = []
      
      i = 0
      tag_list = []
      for tag in deployment_object[0]['metadata']['tags']:
        if deployment_object[0]['metadata']['tags'][i]['key'] != tag_body['key']:
          tag_list.append(tag)
        i = i + 1
      tag_list.append(tag_body)

      body = {
        "metadata": {
          "tags": tag_list
        },
        "prune_orphans": False
      }
      ElasticDeployments.update_deployment_byid(deployment_object[0]['id'], body)
    results['changed'] = False
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
