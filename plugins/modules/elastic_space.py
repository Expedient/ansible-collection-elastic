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
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}
                
import json

def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        space_name=dict(type='str', required=True),
        space_description=dict(type='str', default="None"),
        space_id=dict(type='str', required=True),
        disabledFeatures=dict(type='str', default=None),
        initials=dict(type='str', default=None),
        color=dict(type='str', default=None),
        state=dict(type='str', default='present')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True
                            )
    
    kibana = Kibana(module)
    results['changed'] = False
    space_name = module.params.get('space_name')
    space_description = module.params.get('space_description')
    space_id = module.params.get('space_id')
    disabledFeatures = module.params.get('disabledFeatures')
    initials = module.params.get('initials')
    color = module.params.get('color')
    state = module.params.get('state')
    
    if space_name and state == "present":
      space_object = kibana.create_space(space_id, space_name, space_description,disabledFeatures, initials, color)

    if space_object != "":
      results['space_status'] = "Space Object Found"
      results['space_object'] = space_object
    else:
      results['space_status'] = "No Space Object was returned, check your Space Object Info"
      results['space_object'] = None
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()