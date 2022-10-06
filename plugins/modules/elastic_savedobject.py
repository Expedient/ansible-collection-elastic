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
        object_name=dict(type='str'),
        object_id=dict(type='str', default=None),
        search_string=dict(type='str'),
        object_attributes=dict(type='json'),
        space_id=dict(type='str', default="default"),
        object_type=dict(type='str', default="default"),
        overwrite=dict(type='bool', default=True),
        deployment_info=dict(type='dict', default=None),
        createNewCopies=dict(type='bool', default=False),
        state=dict(type='str', default='present')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True
                            ,mutually_exclusive=[(('object_name','search_string'),'object_attributes')]
                            ,required_one_of=[('object_name','search_string','object_attributes','object_id')]
                            )
    
    kibana = Kibana(module)
    results['changed'] = False
    object_name = module.params.get('object_name')
    object_id = module.params.get('object_id')
    search_string = module.params.get('search_string')
    object_attributes = module.params.get('object_attributes')
    overwrite = module.params.get('overwrite')
    createNewCopies = module.params.get('createNewCopies')
    space_id = module.params.get('space_id')
    object_type = module.params.get('object_type')
    state = module.params.get('state')

    saved_object = None
    
    if (object_name or object_id) and state == "present":
      saved_object_info = kibana.get_saved_object(object_type = object_type, object_id = object_id, object_name = object_name, space_id = space_id)
      saved_object = kibana.export_saved_object(object_type = object_type, object_id = saved_object_info['id'], space_id = space_id)

    if search_string and state == "present":
      if search_string == "None":
        search_string == ""
      saved_object = kibana.get_saved_objects_list(search_string, object_type, space_id = space_id)     

    if object_attributes and state == "absent":

      saved_object = kibana.import_saved_object(object_attributes, space_id = space_id, createNewCopies=createNewCopies, overwrite=overwrite)

    if object_attributes and state == "update":
      saved_object_info = kibana.get_saved_object(object_type = object_type, object_id = object_id, object_name = object_name, space_id = space_id)
      saved_object_id = saved_object_info['id']
      saved_object = kibana.update_saved_object(object_type = object_type, object_id = saved_object_id, object_name = object_name, space_id = space_id, object_attributes = object_attributes)

    if saved_object != "":
      results['object_status'] = "Saved Object Found"
      results['saved_object'] = saved_object
    else:
      results['object_status'] = "No Saved Object was returned, check your Saved Object Info"
      results['saved_object'] = None
      
    module.exit_json(**results)

if __name__ == "__main__":
    main()