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

module: elastic_connector_report

author: Ian Scott

short_description: Create a Connector Report for a Deployment

description: 
  - Create a Connector Report for a Deployment

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

'''
from ansible.module_utils.basic import AnsibleModule
import json
import datetime

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

results = {}
                
def main():

    module_args=dict(    
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_info=dict(type='dict', default=None),
        kibana_url=dict(type='str')
    )
    
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)

    ece = ECE(module)
    results['changed'] = False
    
    #results['pre_connector_list'] = connector_list
    
    all_deployment_info = ece.get_clusters()
    for each_deployment in all_deployment_info:
      if each_deployment['name'] in ['logging-and-metrics','security-cluster','admin-console-elasticsearch']:
        print(str(time_now) + ": Skipping " + each_deployment['name'])
        continue
      for resource in each_deployment['resources']:
        if resource['kind'] == 'kibana':
          deployment_kibana_ref_id = resource['ref_id']
      current_deployment_info = {
        "deployment_id": each_deployment['id'],
        "deployment_name": each_deployment['name'],
        "resource_type": "kibana",
        "ref_id": deployment_kibana_ref_id,
        "version": ""
      }
      module.params['ece_auth'] = ece
      module.params['deployment_info'] = current_deployment_info
      kibana = Kibana(module)
      connector_list = kibana.get_all_connectors()
      cluster_object = ece.get_deployment_byid(each_deployment['id'])
      #cluster_object = ece.get_clusters_by_name(each_deployment['name'])
      
      for kibana_resource in cluster_object['resources']['kibana']:
        if 'aliased_url' in kibana_resource['info']['metadata']:
          kibana_url = kibana_resource['info']['metadata']['aliased_url']
        elif 'service_url' in kibana_resource['info']["metadata"]:
          kibana_url = kibana_resource['info']["metadata"]['service_url']
            
      if kibana_url:
        i=0
        for each_connector in connector_list:
          if 'config' in each_connector:
            if 'headers' in each_connector['config']:
              if  each_connector['config']['headers'] is not None and 'X-Alert-URL' in each_connector['config']['headers'] :
                if kibana_url.find(each_connector['config']['headers']['X-Alert-URL']) > -1:
                  connector_list[i]['connector_status'] = "The connector X-Alert-URL is correct"
                else: 
                  connector_list[i]['connector_status'] = "ERROR: The connector X-Alert-URL is NOT correct"
              else:
                connector_list[i]['connector_status'] = "The connector has no X-Alert-URL"
            else:
              connector_list[i]['connector_status'] = "The connector has no header"
          else:
            connector_list[i]['connector_status'] = "The connector has no config"
          i=i+1
        
      results[each_deployment['name'] + '_connector_list'] = connector_list
      time_now = datetime.datetime.now()
      print(str(time_now) + ": Completed " + each_deployment['name'])
  
    module.exit_json(**results)

if __name__ == "__main__":
    main()
