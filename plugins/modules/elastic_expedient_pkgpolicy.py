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

module: elastic_detection_rule

author: Ian Scott

short_description: Activate Security Rule such as Endpoint Security

description: 
  - Activate Security Rule such as Endpoint Security

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
  agent_policy_name: 
    description: Name of Agent Policy
    type: str
  agent_policy_id: 
    description: ID of Agent Policy
    type: str
  integration_title:
    description: Title of Integration
    type: str
  integration_ver:
    description: Title of Integration
    type: str
  integration_name=dict(type='str'),
  pkg_policy_name=dict(type='str', required=True),
  pkg_policy_desc=dict(type='str'),
  pkg_policy_vars=dict(type='json'),
  integration_settings=dict(type='dict'),
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
        integration_title=dict(type='str'),
        integration_ver=dict(type='str'),
        integration_name=dict(type='str'),
        pkg_policy_name=dict(type='str', required=True),
        pkg_policy_desc=dict(type='str'),
        pkg_policy_vars=dict(type='json'),
        namespace=dict(type='str', default='default'),
        state=dict(type='str', default='present'),
        integration_settings=dict(type='dict'),
        deployment_info=dict(type='dict', default=None)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True,
                            mutually_exclusive=[('agent_policy_name', 'agent_policy_id')],
                            required_one_of=[('agent_policy_name', 'agent_policy_id')],
                            required_together=[('integration_ver','integration_name')]
                          )
    
    state = module.params.get('state')
    agent_policy_name = module.params.get('agent_policy_name')
    agent_policy_id = module.params.get('agent_policy_id')
    integration_title = module.params.get('integration_title')
    integration_ver = module.params.get('integration_ver')
    integration_name = module.params.get('integration_name')
    pkg_policy_name = module.params.get('pkg_policy_name')
    pkg_policy_desc = module.params.get('pkg_policy_desc')
    pkg_policy_vars = module.params.get('pkg_policy_vars')
    namespace = module.params.get('namespace')
    integration_object = {}
    integration_settings = module.params.get('integration_settings') # inputs policy settings only, aka Defaults
    integration_vars = {}
    
    if integration_settings:
      if 'integration_vars' in integration_settings:
        integration_vars = integration_settings['integration_vars']
        integration_settings.pop('integration_vars')
    
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
    
    if ( integration_title or integration_name ):
      integration_object = kibana.check_integration(integration_title, integration_name)
    
    if (( integration_name and integration_ver and integration_title ) and (integration_object == None or integration_object == "")):
      results['integration_status'] = "No integration found, but Integration Name, Version, and Title found"
      integration_object = {
        'name': integration_name,
        'title': integration_title,
        'version': integration_ver
      }
    
    if integration_object == None or integration_object == "":
      results['integration_status'] = 'Integration title is not valid and integration name and integration version are not found'
      results['changed'] = False
      module.exit_json(**results) 
    
    if state == "present":
      body = {
        "keepPoliciesUpToDate": False
      }
      integration_object = kibana.update_integration(
          integration_name = integration_object['name'], 
          integration_version=integration_object['version'], 
          body = body)
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
          pkg_policy_object = kibana.create_pkg_policy(pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace, pkg_policy_vars)
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
        if pkg_policy_object['package']['name'] == 'synthetics':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
              applied_defaults = True
              pkg_policy_object['inputs'][i]['enabled'] = False
              if policy_input['type'] == 'synthetics/http' and integration_vars['type'] == "synthetics/http":
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'http':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                    pkg_policy_object['inputs'][i]['streams'][j]['vars']['urls']['value'] = integration_vars['target_url']
                  j=j+1
                pkg_policy_object['inputs'][i]['enabled'] = False
              if policy_input['type'] == 'synthetics/tcp' and integration_vars['type'] == "synthetics/tcp":
                pkg_policy_object['inputs'][i]['enabled'] = False
              if policy_input['type'] == 'synthetics/icmp' and integration_vars['type'] == "synthetics/icmp":
                pkg_policy_object['inputs'][i]['enabled'] = True
                k = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'icmp':
                    pkg_policy_object['inputs'][i]['streams'][k]['enabled'] = True
                    pkg_policy_object['inputs'][i]['streams'][k]['vars']['hosts']['value'] = integration_vars['target_server']
                  k=k+1
              if policy_input['type'] == 'synthetics/browser' and integration_vars['type'] == "synthetics/browser":
                pkg_policy_object['inputs'][i]['enabled'] = False
            i = i+1    
            
        if pkg_policy_object['package']['name'] == 'winlog':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
              applied_defaults = True
              if policy_input['type'] == 'winlog':
                pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'winlog.winlog':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  j = j + 1
              if policy_input['type'] == 'httpjson':
                pkg_policy_object['inputs'][i]['enabled'] = False
                j = 0
                for stream in policy_input['streams']:
                  if stream['data_stream']['dataset'] == 'winlog.winlog':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  j = j + 1
            i = i+1    
            
        if pkg_policy_object['package']['name'] == 'osquery_manager':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            applied_defaults = True
            pkg_policy_object['inputs'][i]['streams'] = []
            if 'vars' in pkg_policy_object['inputs'][i]:
              pkg_policy_object['inputs'][i].pop('vars')
            if 'config' in pkg_policy_object['inputs'][i]:
              pkg_policy_object['inputs'][i].pop('config')
            i = i+1  
          
        if pkg_policy_object['package']['name'] == 'system':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'logfile' or \
                  policy_input['type'] == 'winlog':
                  if 'service' in integration_vars:
                    if integration_vars['service'] == 'SIEM':
                      pkg_policy_object['inputs'][i]['enabled'] = True
                if policy_input['type'] == 'system/metrics':
                    pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False      
                  if 'service' in integration_vars:
                    if integration_vars['service'] == 'SIEM':
                      if stream['data_stream']['dataset'] == 'system.auth' or \
                        stream['data_stream']['dataset'] == 'system.syslog' or \
                        stream['data_stream']['dataset'] == 'system.application' or \
                        stream['data_stream']['dataset'] == 'system.security' or \
                        stream['data_stream']['dataset'] == 'system.system':
                        pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True

                  if stream['data_stream']['dataset'] == 'system.cpu' or \
                    stream['data_stream']['dataset'] == 'system.diskio' or \
                    stream['data_stream']['dataset'] == 'system.filesystem' or \
                    stream['data_stream']['dataset'] == 'system.fsstat' or \
                    stream['data_stream']['dataset'] == 'system.load' or \
                    stream['data_stream']['dataset'] == 'system.memory' or \
                    stream['data_stream']['dataset'] == 'system.network' or \
                    stream['data_stream']['dataset'] == 'system.process' or \
                    stream['data_stream']['dataset'] == 'system.process.summary' or \
                    stream['data_stream']['dataset'] == 'system.socket_summary' or \
                    stream['data_stream']['dataset'] == 'system.uptime':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  j=j+1
            i = i+1      

        if pkg_policy_object['package']['name'] == 'windows':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'winlog':
                  if 'service' in integration_vars:
                    if integration_vars['service'] == 'SIEM':
                      pkg_policy_object['inputs'][i]['enabled'] = True
                if policy_input['type'] == 'windows/metrics':
                  pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0

                for stream in policy_input['streams']:
                  pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if 'service' in integration_vars:
                    if integration_vars['service'] == 'SIEM':
                      if stream['data_stream']['dataset'] == 'windows.forwarded' or \
                        stream['data_stream']['dataset'] == 'windows.powershell' or \
                        stream['data_stream']['dataset'] == 'windows.powershell_operational' or \
                        stream['data_stream']['dataset'] == 'windows.sysmon_operational':
                          pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  if stream['data_stream']['dataset'] == 'windows.service':
                    pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True
                  j=j+1
            i = i+1

        if pkg_policy_object['package']['name'] == 'linux':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            pkg_policy_object['inputs'][i]['enabled'] = False
            if 'type' in policy_input:
                applied_defaults = True
                if policy_input['type'] == 'system/metrics' or \
                  policy_input['type'] == 'linux/metrics':
                    pkg_policy_object['inputs'][i]['enabled'] = True
                j = 0
                for stream in policy_input['streams']:
                  pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = False
                  if stream['data_stream']['dataset'] == 'linux.service' or \
                    stream['data_stream']['dataset'] == 'linux.users' or \
                    stream['data_stream']['dataset'] == 'linux.network_summary' or \
                    stream['data_stream']['dataset'] == 'linux.socket':
                      pkg_policy_object['inputs'][i]['streams'][j]['enabled'] = True     
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

        if pkg_policy_object['package']['name'] == 'panw':
          i = 0
          for policy_input in pkg_policy_object['inputs']:
            if 'type' in policy_input:
                applied_defaults = True
                pkg_policy_object['inputs'][i]['enabled'] = False
                if policy_input['type'] == 'udp':
                    pkg_policy_object['inputs'][i]['enabled'] = True
                    j = 0
                    for stream in policy_input['streams']:
                      if 'internal_zones' in stream['vars']:
                        pkg_policy_object['inputs'][i]['streams'][j]['vars']['internal_zones']['value'].append("Customer-Private")
                      if 'syslog_host' in stream['vars']:
                        pkg_policy_object['inputs'][i]['streams'][j]['vars']['syslog_host']['value'] = "0.0.0.0" 
                        
                      j=j+1
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
      integration_object = kibana.update_integration(
          integration_name = integration_object['name'], 
          integration_version=integration_object['version'], 
          body = body)
      results['pkg_policy_object_update'] = pkg_policy_info

    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
