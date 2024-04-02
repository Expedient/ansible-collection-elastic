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
  query_data:
    index: 
      description:
        - index
      required: true
    operation:
      description:
        - operation
      required: true
    body:
      description:
        - body
      required: true
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

import csv
import json

results = {}

def main():

    query_data=dict(
      index=dict(type='str', required=True),
      operation=dict(type='str',required=True),
      body=dict(type='str',required=True)
    )
    
    module_args=dict(   
        host=dict(type='str',required=True),
        port=dict(type='int', default=9243),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_info=dict(type='dict', default=None),
        index=dict(type='str', required=True),
        operation=dict(type='str',required=True),
        body=dict(type='str',required=True)
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results['changed'] = False
    index = module.params.get('index')
    operation = module.params.get('operation')
    body = module.params.get('body')
    
    elastic = Elastic(module)
    
    document_list = elastic.get_data(index, operation, body)
  
    results['document_list'] = document_list
    scroll_id = document_list.get('_scroll_id')
    document_list_response = document_list.get('response')
    document_list_all = []
    if document_list_response:
      while document_list_response['hits'].get('hits') != []:  
        document_list = elastic.scroll("_search", scroll_id, "5m")
        document_list_all.append(document_list)
        
    else:
      while document_list['hits'].get('hits') != []:  
        document_list = elastic.scroll("_search", scroll_id, "5m")
        for hit in document_list['hits']['hits']:
          document_list_all.append(hit)
    
    if document_list_all:
      hits_file = open("MyOtherFile.txt", "w")
      csv_writer = csv.writer(hits_file)

      document_list_hits_hits = document_list_response['hits'].get('hits')
      count = 0

      for document_list_hit in document_list_hits_hits:
        if count == 0:
          header = document_list_hit['fields'].keys()
          csv_writer.writerow(header)
          count += 1
        
        for item in document_list_hit['fields'].items():
          if type(document_list_hit['fields'][item[0]]) is list:
            if len(document_list_hit['fields'][item[0]]) > 1:
              for element_value in document_list_hit['fields'][item[0]]:
                element_value_all = element_value + "||" + element_value_all
              document_list_hit['fields'][item[0]] = element_value_all
            else:
              document_list_hit['fields'][item[0]] = document_list_hit['fields'][item[0]][0] 
        
        csv_writer.writerow(document_list_hit['fields'].values())

    hits_file.close()
    file1 = open("MyFile.txt", "w") 
    file1.write(str(document_list))
    file1.close()
    
    module.exit_json(**results)

if __name__ == "__main__":
    main()