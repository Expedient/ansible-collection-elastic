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
#from ansible.module_utils.basic import *

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
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        state=dict(type='str', default='present'),
        active=dict(type='bool', default=True),
        security_rule_name=dict(type='str')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    
    state = module.params.get('state')
    security_rule_name = module.params.get('security_rule_name')
    active = module.params.get('active')
    
    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True

    kibana = Kibana(module)
    if state == "present":
      if active == True:
        sec_rule_info = kibana.activate_security_rule(security_rule_name)
        if sec_rule_info == security_rule_name + ': Rule is already enabled':
          results['changed'] = False
        results['sec_rule_info'] = sec_rule_info
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
