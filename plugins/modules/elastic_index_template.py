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

module: elastic_index_lifecycle_policy_info

author: Ian Scott

short_description: Get information on an Elastic LifeCycle Policy

description: 
  - Get information on an Elastic LifeCycle Policy

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
  index_template: 
    description: Name of index template
    type: str
  state:
    description: Index Template state
    type: str
  index_patterns:
    description: index_patterns
    type: list
  index_patterns_action:
    description: index_patterns operation (add/remove)
    type: str
  composed_of:
    description: composed_of
    type: list
  composed_of_action:
    description: composed_of operation (add/remove)
    type: str
  priority:
    description: priority
    type: int
  data_stream:
    description: data_stream
    type: dict
  template:
    description: data_stream
    type: dict
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
        deployment_info=dict(type='dict', default=None),
        index_template=dict(type='str'),
        state=dict(type='str', default='present'),
        index_patterns=dict(type='list'),
        index_patterns_action=dict(type='str', default='add'),
        composed_of=dict(type='list'),
        composed_of_action=dict(type='str', default='add'),
        template_priority=dict(type='int', default=100),
        index_priority=dict(type='int', default=100),
        data_stream=dict(type='dict'),
        template=dict(type='dict')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results['changed'] = False
    
    elastic = Elastic(module)
    index_template_name = module.params.get('index_template')
    index_priority = module.params.get('index_priority')
    state = module.params.get('state')
    index_patterns = module.params.get('index_patterns')
    index_patterns_action = module.params.get('index_patterns_action')
    composed_of = module.params.get('composed_of')
    composed_of_action = module.params.get('composed_of_action')
    template_priority = module.params.get('template_priority')
    data_stream = module.params.get('data_stream')
    template = module.params.get('template')
    
    if index_template_name and state == 'present':
      index_template_object = elastic.get_index_template(index_template_name)
      results['index_template_object'] = index_template_object
      if index_template_object:
        if index_patterns:
          if index_patterns_action == "add":
            index_template_object['index_template']['index_patterns'] += index_patterns
        if composed_of:
          if composed_of_action == "add":
            for component_template in composed_of:
              component_template_object = elastic.get_component_template(component_template)
              if component_template_object:
                component_exists = False
                for existing_component_template in index_template_object['index_template']['composed_of']:
                  if existing_component_template == component_template:
                    component_exists = True
                if component_exists == False:
                  index_template_object['index_template']['composed_of'] += [component_template]
        if template_priority:
          index_template_object['index_template']['priority'] = template_priority
        if data_stream:
          index_template_object['index_template']['data_stream'] = data_stream
        if template:
          index_template_object['index_template']['template'] = template
        if index_priority:
          index_template_object['priority'] = index_priority
        updated_index_template_object = elastic.update_index_template(index_template_name, index_template_object['index_template'])
        results['updated_index_template_object'] = updated_index_template_object
        results['index_template_status'] = "Index Template Updated"
        
    
    results['updated_index_template_object'] = index_template_object
    module.exit_json(**results)

if __name__ == "__main__":
    main()