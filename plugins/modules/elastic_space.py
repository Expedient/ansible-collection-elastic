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

module: elastic_space

author: Ian Scott

short_description: Create an Elastic Space.

description: 
  - Create an Elastic Space.

requirements:
  - python3

options:
  host:
    description: ECE Host
    type: str
  port:
    description: ECE Port
    type: str
  username:
    description: ECE Username
    type: str
  password:
    description: ECE Password
    type: str
  deployment_info:
    description: Deployment Information
    type: dict
    suboptions:
      deployment_id:
        required: False
        description: ECE Deployment ID
        type: str
      deployment_name:
        required: False
        description: ECE Deployment Name
        type: str
      resource_type:
        description: "Type or Resource, most likely kibana"
        type: str
      ref_id:
        description: "REF ID for kibana cluster, most likely main-kibana"
        type: str
      version:
        description: Deployment Kibana Version
        type: str
      space_name: Space name
      space_description: Description of Space
      space_id: Space ID. Used in urls.
      disabledFeatures: List of Features to be disabled within this space
      initials: Initials of Space
      color: Color of Space Icon Background
'''
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
                
def main():

    module_args=dict(    
        host=dict(type='str'),
        port=dict(type='int', default=12443),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        space_name=dict(type='str', required=True),
        space_description=dict(type='str', default="None"),
        space_id=dict(type='str', required=True),
        disabledFeatures=dict(type='list'),
        initials=dict(type='str', default=None),
        color=dict(type='str', default=None),
        imageUrl=dict(type='str', default=None),
        deployment_info=dict(type='dict', default=None),
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
    imageUrl = module.params.get('imageUrl')
    state = module.params.get('state')
    
    space_object = None
    
    if space_id and state == "present":
      
      space_object = kibana.get_space(space_id)
      results['space_status'] = "Space Object Found"
      
      if space_object == None:
        space_object = kibana.create_space(space_id, space_name, space_description, disabledFeatures, initials, color, imageUrl)
        results['space_status'] = "Space Object Created"
      else:
        space_object = kibana.update_space(space_id, space_name, space_description, disabledFeatures, initials, color, imageUrl)
        results['space_status'] = "Space Object Updated"
        
    module.exit_json(**results)

if __name__ == "__main__":
    main()