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

module: elastic_settings_update

author: Ian Scott

short_description: Update Elasticsearch settings.

description: 
  - Update Elasticsearch settings such as routing, metadata, etc.

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
      elastic_setting:
        state: persistent or transient
        var: elastic var name
        value: elastic var value
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

    elastic_settings_spec=dict(
      state=dict(type='str', choices=['persistent', 'transient']),
      var=dict(type='str',required=True),
      value=dict(type='int',required=True)
    )
    
    module_args=dict(   
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_info=dict(type='dict', default=None),
        elastic_settings=dict(type='list', required=False, elements='dict', options=elastic_settings_spec)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results['changed'] = False
    elastic_settings = module.params.get('elastic_settings')
    
    elastic = Elastic(module)
    body = {
      "persistent": {},
      "transient": {}
    }
    for elastic_setting in elastic_settings:
      body[elastic_setting['state']][elastic_setting['var']] = elastic_setting['value']
    
    elastic_settings_object = elastic.update_settings(body)
  
    results['elastic_settings_object'] = elastic_settings_object
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
