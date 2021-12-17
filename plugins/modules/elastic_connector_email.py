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
import json

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
        connector_name=dict(type='str', required=True),
        connector_type=dict(type='str', required=True),
        connector_sender=dict(type='str', required=True),
        connector_host=dict(type='str', required=True),
        connector_port=dict(type='str', required=True),
        connector_headers=dict(type='str')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    kibana = Kibana(module)
    results['changed'] = True
    connector_name = module.params.get('connector_name')
    connector_type = module.params.get('connector_type')
    connector_sender = module.params.get('connector_sender')
    connector_host = module.params.get('connector_host')
    connector_port = module.params.get('connector_port')
    
    connector_info = None
    if connector_type == "email":
      config = {
        "hasAuth": False,
        "from": connector_sender,
        "host": connector_host,
        "port": connector_port
      }
      connector_exists = kibana.get_connector_byname(connector_name)
      
      if not connector_exists:
        connector_info = kibana.create_connector(connector_name, connector_type, config)
        results['connector_status'] = "Create Email Connector"
        results['connector_object'] = connector_info
      else:
        results['connector_status'] = "Connector already exists by that name"
        results['connector_object'] = connector_exists
    else:
      results['connector_status'] = "Create Email Connector Failed, set connector_type to webhook"
      results['connector_object'] = connector_info
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()