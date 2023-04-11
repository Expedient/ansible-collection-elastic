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

module: elastic_kibana_settings

author: Ian Scott

short_description: Set Elastic Kibana Settings

description: 
  - Set Elastic Kibana Settings

requirements:
  - python3

options:
      host: ECE Host or Deployment Host
      port: ECE Port or Deployment Port
      username: ECE Username or Deployment Username
      password: ECE Password or Deployment Password
      deployment_info: (when using ECE host:port and credentials)
        deployment_id: ECE Deployment ID
        deployment_name: ECE Deployment Name
        resource_type: kibana
        ref_id: REF ID for kibana cluster, most likely main-kibana
        version: Deployment Kibana Version
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

    elastic_index_lifecycle_policy_spec=dict(
      index_lifecycle_policy_name=dict(type='str', required=True),
      settings=dict(type='dict', default="None")
    ) 
    elastic_role_mapping_spec=dict(
        role_mapping_name=dict(type='str', required=True),
        enable_mapping=dict(type='bool', default=True),
        assigned_roles=dict(type='list', required=True),
        role_mapping_rules=dict(type='dict', required=True),
        metadata=dict(type='dict')
    )

    module_args=dict(   
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        elastic_index_lifecycle_policy_settings=dict(type='list', required=False, options=elastic_index_lifecycle_policy_spec),
        elastic_role_mapping_settings=dict(type='list', required=False, options=elastic_role_mapping_spec),
        state=dict(type='str', default='present'),
        deployment_info=dict(type='dict', default=None)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results['changed'] = False
    
    elastic = Elastic(module)

    elastic_index_lifecycle_policy_settings = module.params.get('kibana_index_lifecycle_policy_settings')
    elastic_role_mapping_settings = module.params.get('elastic_role_mapping_settings')

    if elastic_index_lifecycle_policy_settings:
      results['elastic_index_lifecycle_status'] = "Elastic Index Lifecycle Policy found"
      elastic_index_lifecycle_policy_object = elastic.get_index_lifecycle_policy(elastic_index_lifecycle_policy_settings['index_lifecycle_policy_name'])
      results['index_lifecycle_policy_object'] = elastic_index_lifecycle_policy_object
      if not module.check_mode:
        elastic_index_lifecycle_policy_object = elastic.update_index_lifecycle_policy(elastic_index_lifecycle_policy_settings['index_lifecycle_policy_name'], elastic_index_lifecycle_policy_settings['settings'])
        results['index_lifecycle_policy_object'] = elastic_index_lifecycle_policy_object
        results['changed'] = True
    if elastic_role_mapping_settings:
      role_mapping_object = elastic.create_role_mapping(
        elastic_role_mapping_settings['role_mapping_name'], 
        elastic_role_mapping_settings['assigned_roles'], 
        elastic_role_mapping_settings['role_mapping_rules'], 
        elastic_role_mapping_settings['metadata'], 
        elastic_role_mapping_settings['enable_mapping'])
      results['userrole_status'] = "Role Mapping Created"
      results['role_mapping_object'] = role_mapping_object
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
