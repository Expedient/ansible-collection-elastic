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

DOCUMENTATION='''

Add an elasticseach data lifecycle policy to deployment

Input example:

elastic_deployment_info:
  deployment_id: "{{ deployment_id }}"
  deployment_name: "{{ deployment_name }}"
  resource_type: elasticsearch
  ref_id: "{{ cluster_kibana_info.deployment_object.resources.elasticsearch[0].ref_id }}"

      host: "{{ ece_host }}"
      port: "{{ ece_port }}"
      username: "{{ ece_username }}"
      password: "{{ ece_password }}"
      deployment_info: "{{ elastic_deployment_info }}"
      index_lifecycle_policy_name: logs
      settings: 
        policy:
          phases:
            hot:
              min_age: 0ms
              actions:
                rollover:
                  max_size: 100gb
                  max_primary_shard_size: 50gb
                  max_age: 7d
            delete:
              min_age: 30d
              actions:
                delete:
                  delete_searchable_snapshot: true

'''

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
#from ansible.module_utils.basic import *

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

results = {}

def main():

    module_args=dict(   
        host=dict(type='str'),
        port=dict(type='int', default=12443),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        index_lifecycle_policy_name=dict(type='str'),
        settings=dict(type='dict'),
        deployment_info=dict(type='dict', default=None)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results['changed'] = False
    
    elastic = Elastic(module)
    index_lifecycle_policy_name = module.params.get('index_lifecycle_policy_name')
    new_settings = module.params.get('settings')
    
    if index_lifecycle_policy_name and new_settings:
      results['elastic_index_lifecycle_status'] = "Elastic Index Lifecycle Policy found"
      elastic_index_lifecycle_policy_object = elastic.update_index_lifecycle_policy(index_lifecycle_policy_name, new_settings)
      results['index_lifecycle_policy_object'] = elastic_index_lifecycle_policy_object
      results['changed'] = True
    else:
      results['elastic_index_lifecycle_status'] = "Elastic Index Lifecycle Policy NOT found"
      results['index_lifecycle_policy_object'] = ""
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
