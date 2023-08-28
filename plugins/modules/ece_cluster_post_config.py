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

module: ece_cluster_post_config

author: Ian Scott

short_description: Create Elastic Deployment Alias from ECE

description: 
  - Create Elastic Deployment Alias from ECE

requirements:
  - python3

options:

  host:
    description: ECE Host
    type: str

  port:
    description: ECE Port
    type: str

  deployment_name:
    description: 
    - Name of Deployment
    - Required if deployment_id is blank
    type: str

  deployment_id:
    description: 
    - Deployment ID
    - Required if deployment_name is blank
    type: str

  username:
    description: ECE Username
    type: str

  password:
    description: ECE Password
    type: str

  alias_name:
    description: Deployment Alias String
    type: str
    

'''
from ansible.module_utils.basic import AnsibleModule

import time

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

import json

results = {}    
    
def main():

    module_args=dict(
        host=dict(type='str'),
        port=dict(type='int', default=12443),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True),   
        verify_ssl_cert=dict(type='bool', default=True),
        deployment_name=dict(type='str'),
        deployment_id=dict(type='str', default=None),
        alias_name=dict(type='str', required=True),
        logging_dest=dict(type='str', required=True),
        metrics_dest=dict(type='str', required=True),
        logging_ref_id=dict(type='str', default="elasticsearch"),
        metrics_ref_id=dict(type='str', default="elasticsearch")
    )
    argument_dependencies = []
        #('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
        #('alert-type', 'metrics_threshold', ('conditions'))
    
    module = AnsibleModule(argument_spec=module_args, required_if=argument_dependencies, supports_check_mode=True)
    
    deployment_name = module.params.get('deployment_name')
    deployment_id = module.params.get('deployment_id')
    alias_name = module.params.get('alias_name')
    logging_dest = module.params.get('logging_dest')
    metrics_dest = module.params.get('metrics_dest')
    logging_ref_id = module.params.get('logging_ref_id')
    metrics_ref_id = module.params.get('metrics_ref_id')
    results = { 'changed': True }
        
    ElasticDeployments = ECE(module)
    
    if deployment_id:
      deployment_object = [ElasticDeployments.get_deployment_byid(deployment_id)]
    elif deployment_name:
      deployment_object = [ElasticDeployments.get_deployment_info(deployment_name)]

    logging_object = [ElasticDeployments.get_deployment_info(logging_dest)]
    metrics_object = [ElasticDeployments.get_deployment_info(metrics_dest)]

    if len(deployment_object) == 1:
      deployment_object = deployment_object[0]
      update_body = {
        'alias': alias_name,
        'prune_orphans': False,
        'resources': {
          'elasticsearch': [
            {
              'region':  deployment_object['resources']['elasticsearch'][0]['region'],
              'ref_id':  deployment_object['resources']['elasticsearch'][0]['ref_id'],
              'plan': deployment_object['resources']['elasticsearch'][0]['info']['plan_info']['current']['plan']
            }
          ],
          'kibana': [
            {
              'region':  deployment_object['resources']['kibana'][0]['region'],
              'ref_id':  deployment_object['resources']['kibana'][0]['ref_id'],
              'elasticsearch_cluster_ref_id':  deployment_object['resources']['elasticsearch'][0]['ref_id'],
              'plan': deployment_object['resources']['kibana'][0]['info']['plan_info']['current']['plan']
            }
          ]
        },
        'settings': {
          'observability': {
            'logging': {
              'destination': {
                'deployment_id': logging_object[0]['resources'][logging_ref_id][0]['id'],
                'ref_id': logging_ref_id
              }
            },
            'metrics': {
              'destination': {
                'deployment_id': metrics_object[0]['resources'][metrics_ref_id][0]['id'],
                'ref_id': metrics_ref_id
              }
            }
          }
        }
      }
      
      ElasticDeployments.update_deployment_byid(deployment_object['id'], update_body)
      
      ElasticDeployments.wait_for_cluster_healthy(deployment_object['id'])
      ElasticDeployments.wait_for_cluster_state(deployment_object['id'], "elasticsearch" ) # Wait for ElasticSearch
      ElasticDeployments.wait_for_cluster_state(deployment_object['id'], "kibana" ) # Wait for Kibana
      deployment_healthy = ElasticDeployments.wait_for_cluster_state(deployment_object['id'], "apm") # If APM is healthy then the deployment is healthy since apm is last to come up
      
      if deployment_healthy == False:
        results['post_config_status'] = "Cluster information may be incomplete because the cluster is not healthy"
      else:
        time.sleep(30)
        
      results['changed'] = True
    else:
      results['changed'] = False
      results['post_config_status'] = "0 or more than 1 deployment was matched with the name " + deployment_name + " or id " + deployment_id
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
