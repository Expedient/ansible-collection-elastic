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
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}

def main():

  kibana_space_adv_settings_spec=dict(
    space_id=dict(type='str', default='default'),
    settings=dict(type='dict'),
  )  

  kibana_userrole_settings_spec=dict(
    role_name=dict(type='str', default='default'),
    body=dict(type='dict', default=1),
  )
  
  kibana_space_spec=dict(
    space_name=dict(type='str', required=True),
    space_description=dict(type='str', default="None"),
    space_id=dict(type='str', required=True),
    disabledFeatures=dict(type='list'),
    initials=dict(type='str', default=None),
    color=dict(type='str', default=None),
  )  
  
  kibana_fleet_pkg_policy_spec=dict(
    pkg_policy_name=dict(type='str', required=True),
    pkg_policy_desc=dict(type='str', default='N/A'),
    integration_name=dict(type='str', required=True),
    integration_title=dict(type='dict', default="None"),   
    integration_ver=dict(type='dict', required=True),
    integration_settings=dict(type='dict', required=False,options=dict(
      integration_vars=dict(type=dict, options=dict(
        service=dict(type='str')
      ))
    ))
  )

  kibana_fleet_agent_policy_spec=dict(
    agent_policy_name=dict(type='str', required=True),
    agent_policy_desc=dict(type='dict', default="None"),
    monitoring=dict(type='list'),
    space_id=dict(type='str', default='default'),
    kibana_fleet_pkg_policy_settings=dict(type='list', required=False, options=kibana_fleet_pkg_policy_spec),
  ) 

  kibana_savedobject_specs=dict(
    object_name=dict(type='str'),
    object_id=dict(type='str'),
    action=dict(type='str', required=True), #import, export, ...
    overwrite=dict(type='bool', default=True),
    createNewCopies=dict(type='bool', default=False),
    space_id=dict(type='str', default='default'),
  )
  
  kibana_default_dashboard_specs=dict(
    object_attributes=dict(type='list'),
    overwrite=dict(type='bool', default=True),
    createNewCopies=dict(type='bool', default=False),
    space_id=dict(type='str', default='default'),
  ) 

  module_args=dict(   
      host=dict(type='str', required=True),
      port=dict(type='int', default=9243),
      username=dict(type='str', required=True),
      password=dict(type='str', no_log=True, required=True),   
      verify_ssl_cert=dict(type='bool', default=True),
      kibana_space_adv_settings=dict(type='dict', required=False, options=kibana_space_adv_settings_spec),
      kibana_userrole_settings=dict(type='dict', required=False, options=kibana_userrole_settings_spec),
      kibana_space_settings=dict(type='dict', required=False, options=kibana_space_spec),
      kibana_fleet_agent_policies=dict(type='list', required=False, options=kibana_fleet_agent_policy_spec),
      kibana_savedobject_settings=dict(type='list', required=False, options=kibana_savedobject_specs),
      kibana_default_dashboards=dict(type='dict', required=False, options=kibana_default_dashboard_specs),
      state=dict(type='str', default='present'), # present, absent
      deployment_info=dict(type='dict', default=None)
  )
  
  argument_dependencies = []
      #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
      #('alert-type', 'metrics_threshold', ('conditions'))
  
  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

  results['changed'] = False
  
  kibana = Kibana(module)
  kibana_space_adv_settings = module.params.get('kibana_space_adv_settings')
  kibana_userrole_settings = module.params.get('kibana_userrole_settings')
  kibana_space_settings = module.params.get('kibana_space_settings')
  kibana_savedobject_settings = module.params.get('kibana_savedobject_settings')
  kibana_default_dashboards = module.params.get('kibana_default_dashboards')
  kibana_fleet_agent_policies = module.params.get('kibana_fleet_agent_policies')
  state = module.params.get('state')

  if kibana_space_settings:
    space_object = kibana.get_space(kibana_space_settings['space_id'])
    if space_object != None:
      results['space_status'] = "Space Object Found"
    if space_object == None and not module.check_mode:
      space_object = kibana.create_space(
        kibana_space_settings.get('space_id'), 
        kibana_space_settings.get('space_name'), 
        kibana_space_settings.get('space_description'), 
        kibana_space_settings.get('disabledFeatures'), 
        kibana_space_settings.get('initials'),
        kibana_space_settings.get('color')
        )
      results['space_status'] = "Space Object Created"
    results['space_object'] = space_object
  if kibana_space_adv_settings:
    kibana_settings = kibana.update_kibana_settings(
      kibana_space_adv_settings.get('settings'), 
      space_id = kibana_space_adv_settings.get('space_id')
      )
    results['kibana_settings_object'] = kibana_settings
  if kibana_userrole_settings:
    userrole_object = kibana.get_userrole(kibana_userrole_settings.get('role_name'))
    results['userrole_status'] = "User Role Object Info"
    results['userrole_object'] = userrole_object
    if userrole_object == None and not module.check_mode:
      userrole_object = kibana.create_userrole(
        kibana_userrole_settings.get('role_name'), 
        kibana_userrole_settings.get('body'))
      results['userrole_status'] = "User Role Object Created"
      results['userrole_object'] = userrole_object
  if kibana_default_dashboards:
    saved_object = None
    if kibana_default_dashboards['object_attributes'] \
      and state == "present":

      saved_object = kibana.import_saved_object(
        kibana_default_dashboards['object_attributes'], 
        space_id = kibana_default_dashboards['space_id'], 
        createNewCopies = kibana_default_dashboards['createNewCopies'], 
        overwrite = kibana_default_dashboards['overwrite'])
      
  if kibana_savedobject_settings:
    saved_object = None
    
    if (kibana_savedobject_settings['object_name'] or kibana_savedobject_settings['object_id']) \
        and kibana_savedobject_settings['state'] == "present":
      saved_object_info = kibana.get_saved_object(
        object_type = kibana_savedobject_settings['object_type'], 
        object_id = kibana_savedobject_settings['object_id'], 
        object_name = kibana_savedobject_settings['object_name'], 
        space_id = kibana_savedobject_settings['space_id'])
      saved_object = kibana.export_saved_object(
        object_type = kibana_savedobject_settings['object_type'], 
        object_id = saved_object_info['id'], 
        space_id = kibana_savedobject_settings['space_id'])

    if kibana_savedobject_settings['search_string'] \
        and state == "present":
      if kibana_savedobject_settings['search_string'] == "None":
        kibana_savedobject_settings['search_string'] == ""
      saved_object = kibana.get_saved_objects_list(
        kibana_savedobject_settings['search_string'], 
        kibana_savedobject_settings['object_type'], 
        space_id = kibana_savedobject_settings['space_id'])     

    if kibana_savedobject_settings['object_attributes'] \
        and state == "update":
      saved_object_info = kibana.get_saved_object(
        object_type = kibana_savedobject_settings['object_type'], 
        object_id = kibana_savedobject_settings['object_id'], 
        object_name = kibana_savedobject_settings['object_name'], 
        space_id = kibana_savedobject_settings['space_id'])
      saved_object_id = saved_object_info['id']
      saved_object = kibana.update_saved_object(
        object_type = kibana_savedobject_settings['object_type'], 
        object_id = saved_object_id, 
        object_name = kibana_savedobject_settings['object_name'], 
        space_id = kibana_savedobject_settings['space_id'], 
        object_attributes = kibana_savedobject_settings['object_attributes'])

    if saved_object != "":
      results['object_status'] = "Saved Object Found"
      results['saved_object'] = saved_object
    else:
      results['object_status'] = "No Saved Object was returned, check your Saved Object Info"
      results['saved_object'] = None
      
  if kibana_fleet_agent_policies:
    if state == "present":
      for agent_policy in kibana_fleet_agent_policies:
        agent_policy_object = kibana.create_agent_policy()
    

  
  module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
