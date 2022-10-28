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

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

results = {}
                
import json

def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        role_mapping_name=dict(type='str', required=True),
        enable_mapping=dict(type='bool', default=True),
        assigned_roles=dict(type='list'),
        role_mapping_rules=dict(type='dict'),
        metadata=dict(type='dict'),
        state=dict(type='str', default='present')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True
                            )
    
    elastic = Elastic(module)
    results['changed'] = False
    role_mapping_name = module.params.get('role_mapping_name')
    enable_mapping = module.params.get('enable_mapping')
    assigned_roles = module.params.get('assigned_roles')
    role_mapping_rules = module.params.get('role_mapping_rules')
    metadata = module.params.get('metadata')
    state = module.params.get('state')
    
    if role_mapping_name and state == "present":
      
      role_mapping_object = elastic.create_role_mapping(role_mapping_name, assigned_roles, role_mapping_rules, metadata, enable_mapping)
      results['userrole_status'] = "Role Mapping Created"
        
    results['role_mapping_object'] = role_mapping_object
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()