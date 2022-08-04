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
        dashboard_name=dict(type='str'),
        dashboard_attributes=dict(type='json'),
        state=dict(type='str', default='present'),
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True
                            ,mutually_exclusive=[('dashboard_name', 'dashboard_attributes')]
                            ,required_one_of=[('dashboard_name', 'dashboard_attributes')]
                            )
    
    kibana = Kibana(module)
    results['changed'] = False
    dashboard_name = module.params.get('dashboard_name')
    dashboard_attributes = module.params.get('dashboard_attributes')
    state = module.params.get('state')

    if dashboard_name and state == "present":
      dashboard_object_info = kibana.get_saved_object("dashboard", dashboard_name)
      dashboard_object = kibana.export_saved_object("dashboard", dashboard_object_info['id'])

    if dashboard_attributes and state == "absent":
      dashboard_object = kibana.import_saved_object(dashboard_attributes)

    if dashboard_object:
      results['dashboard_status'] = "Dashboard Found"
      results['dashboard_object'] = dashboard_object
    else:
      results['dashboard_status'] = "No Dashboard was returned, check your Dashboard Info"
      results['dashboard_object'] = None
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()