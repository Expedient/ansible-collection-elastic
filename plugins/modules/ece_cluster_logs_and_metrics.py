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

module: ece_cluster_logs_and_metrics

author: Ian Scott

short_description: Update Elastic Deployment Logging and Metrics Settings

description: 
  - Update Elastic Deployment Logging and Metrics Settings

requirements:
  - python3

options:
      host: ECE Host
      port: ECE Port
      deployment_name or deployment_id
      username: ECE Username
      password: ECE Password
      logging_dest: Destination Deployment name for Logging
      metrics_dest: Destination Deployment name for Metrics
      logging_ref_id: Reference ID for Logging
      metrics_ref_id: Reference ID for Metrics

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
    
    if deployment_object:
      update_body = {
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

      body = {
        'settings': {
          'observability': update_body
        },
        'prune_orphans': False
      }
      ElasticDeployments.update_deployment_byid(deployment_object[0]['id'], body)
      
      deployment_healthy = ElasticDeployments.wait_for_cluster_state(deployment_object[0]['id'], "elasticsearch" )
      deployment_healthy = ElasticDeployments.wait_for_cluster_state(deployment_object[0]['id'], "kibana" )
      deployment_healthy = ElasticDeployments.wait_for_cluster_state(deployment_object[0]['id'], "kibana","main-apm")
      
      if deployment_healthy == False:
        results['cluster_data']['msg'] = "Cluster information may be incomplete because the cluster is not healthy"
      else:
        time.sleep(30)
        
    results['changed'] = True
    module.exit_json(**results)

if __name__ == "__main__":
    main()
    
     
