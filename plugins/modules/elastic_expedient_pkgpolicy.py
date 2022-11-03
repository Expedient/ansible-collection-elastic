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

def deep_update(original, updated):
    """
    Attempts to update deeply nested dictionaries + lists
    :param original/the object to be updated:
    :param updated/changes to be applied:
    :return:
    """

    def match_shallow_structure(dictionary_1, dictionary_2):
        """
        utility function to check if all the non-dictionary keys and values in a
        dictionary match those of the other
        :param dictionary_1:
        :param dictionary_2:
        :return:
        """
        shallow_1 = {
            key: value for key, value in dictionary_1.items() if
            not isinstance(value, dict)
        }
        shallow_2 = {
            key: value for key, value in dictionary_2.items() if
            not isinstance(value, dict)
        }
        return shallow_1 == shallow_2

    if isinstance(updated, dict):
        for key, value in updated.items():
            if (isinstance(value, dict) or isinstance(value, list)) and original.get(
                key
            ) is not None:
                deep_update(original.get(key), updated[key])
            else:
                original.update({key: updated[key]})
    elif isinstance(updated, list) and isinstance(original, list):
        if all([isinstance(item, dict) for item in updated]):
            for updated_dictionary_list_item in updated:
                try:
                    deep_update(
                        next(
                            original_dictionary_list_item
                            for original_dictionary_list_item in original
                            if match_shallow_structure(
                                updated_dictionary_list_item,
                                original_dictionary_list_item,
                            )
                        ),
                        updated_dictionary_list_item,
                    )
                except StopIteration:
                    original.append(updated_dictionary_list_item)
        else:
            original += [i for i in updated if i not in original]
    return

def main():

    module_args=dict(   
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        agent_policy_id=dict(type='str'),
        agent_policy_name=dict(type='str'),
        integration_title=dict(type='str', required=True),
        integration_ver=dict(type='str'),
        integration_name=dict(type='str'),
        pkg_policy_name=dict(type='str', required=True),
        pkg_policy_desc=dict(type='str'),
        namespace=dict(type='str', default='default'),
        state=dict(type='str', default='present'),
        integration_settings=dict(type='dict')
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')],
                            required_together=[('integration_ver','integration_name')])
    
    state = module.params.get('state')
    agent_policy_name = module.params.get('agent_policy_name')
    agent_policy_id = module.params.get('agent_policy_id')
    integration_title = module.params.get('integration_title')
    integration_ver = module.params.get('integration_ver')
    integration_name = module.params.get('integration_name')
    pkg_policy_name = module.params.get('pkg_policy_name')
    pkg_policy_desc = module.params.get('pkg_policy_desc')
    namespace = module.params.get('namespace')
    integration_object = {}
    integration_settings = module.params.get('integration_settings') # inputs policy settings only, aka Defaults
    
    if module.check_mode:
        results['changed'] = False
    else:
        results['changed'] = True

    kibana = Kibana(module)
    
    if module.params.get('agent_policy_id'):
      agency_policy_object = kibana.get_agent_policy_byid(agent_policy_id)
    else:
      agency_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    try:
      agent_policy_id = agency_policy_object['id']
      results['agent_policy_status'] = "Agent Policy found."
    except:
      results['agent_policy_status'] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
      results['changed'] = False
      module.exit_json(**results)
    
    if ( integration_title and not ( integration_ver and integration_title )):
      integration_object = kibana.check_integration(integration_title)
    elif ( integration_name and integration_ver and integration_title ) and not integration_object:
      results['integration_status'] = "No integration found, but Integration Name, Version, and Title found"
      integration_object = {
        'name': integration_name,
        'title': integration_title,
        'version': integration_ver
      }
    elif not integration_object and not ( integration_title and integration_ver and integration_name):
      results['integration_status'] = 'Integration Title is not valid and integration name and integration version are not found'
      results['changed'] = False
      module.exit_json(**results) 
    
    if state == "present":
      body = {
        "keepPoliciesUpToDate": False
      }
      integration_object = kibana.update_integration(integration_object['name'], body)
      pkg_policy_object = kibana.get_pkg_policy(pkg_policy_name)
      pkg_policy_object_orig = pkg_policy_object
      applied_defaults = False
      if 'item' in pkg_policy_object:
        pkg_policy_object = pkg_policy_object['item']      
      if pkg_policy_object:
        results['pkg_policy_status'] = "Integration Package found, No package created"
        results['changed'] = False
      else:
        if module.check_mode == False: 
          ### Make sure Integration is not set to "Keep integration policies up to date"
          pkg_policy_object = kibana.create_pkg_policy(pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace)
          pkg_policy_object_orig = pkg_policy_object
          if 'item' in pkg_policy_object:
            pkg_policy_object = pkg_policy_object['item']
          #pkg_policy_object = kibana.upgrade_pkg_policy(pkg_policy_object['id'])
          results['pkg_policy_status'] = "No Integration Package found, Package Policy created"
          results['pkg_policy_object'] = pkg_policy_object
          results['changed'] = True
        else:
          results['pkg_policy_status'] = "No Integration Package found, Package Policy not created because check_mode is set to true"
          results['pkg_policy_object'] = ""
          results['changed'] = False

      if not integration_settings or integration_settings is None:
        if pkg_policy_object['package']['name'] == 'system':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                if policy_input['type'] == 'logfile':
                    pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'winlog':
                    pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'httpjson':
                    pkg_policy_object['inputs'][i]['enabled'] = False
                    #pkg_policy_object['inputs'][i]['vars']['ssl']['value'] = None
                if policy_input['type'] == 'system/metrics':
                  pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'system.security':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.system':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.application':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.auth':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.syslog':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.core':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'system.cpu':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.diskio':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.filesystem':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.fsstat':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.load':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.memory':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.network':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.process':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.process.summary':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.socket_summary':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'system.uptime':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  j=j+1
            i = i+1      

        if pkg_policy_object['package']['name'] == 'windows':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                if policy_input['type'] == 'winlog':
                    pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'httpjson':
                    pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'windows/metrics':
                  pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'windows.service':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'windows.perfmon':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'windows.forwarded':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'windows.powershell':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'windows.powershell_operational':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'windows.sysmon_operational':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  j=j+1
            i = i+1

        if pkg_policy_object['package']['name'] == 'linux':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                if policy_input['type'] == 'system/metrics':
                  pkg_policy_object['inputs'][i]['enabled'] = True
                if policy_input['type'] == 'linux/metrics':
                  pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'linux.service':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'linux.users':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'linux.entropy':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.raid':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.network_summary':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'linux.socket':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True     
                  if stream['data_stream']['dataset'] == 'linux.pageinfo':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.iostat':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.memory':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.ksm':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.conntrack':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  j=j+1
            i = i+1

        if pkg_policy_object['package']['name'] == 'endpoint':
          mode = str(pkg_policy_object['name']).split('-')[-1]
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'config' in policy_input:
                applied_defaults = True
                pkg_policy_object['inputs'][i]['config']['policy']['value']['linux']['behavior_protection']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['linux']['malware']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['linux']['memory_protection']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['behavior_protection']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['malware']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['ransomware']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['memory_protection']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['windows']['antivirus_registration']['enabled'] = True
                pkg_policy_object['inputs'][i]['config']['policy']['value']['mac']['behavior_protection']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['mac']['malware']['mode'] = mode
                pkg_policy_object['inputs'][i]['config']['policy']['value']['mac']['memory_protection']['mode'] = mode
            i = i+1

      if pkg_policy_object == pkg_policy_object_orig and applied_defaults is False:
        results['pkg_policy_object_updated'] = "False"
      else:
        results['pkg_policy_object_updated'] = "True"
      pkg_policy_object_id = pkg_policy_object['id']
      pkg_policy_info = kibana.update_pkg_policy(pkg_policy_object_id, pkg_policy_object)
      body = {
        "keepPoliciesUpToDate": True
      }
      integration_object = kibana.update_integration(integration_object['name'], body)
      results['pkg_policy_object_update'] = pkg_policy_info

    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
