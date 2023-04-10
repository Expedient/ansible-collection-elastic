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

# -*- coding: utf-8 -*-


ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: ece_cluster

short_description: Create modify or delete Elasticsearch clusters in ECE

version_added: '2.9'

author: Mike Garuccio (@mgaruccio)

requirements:
  - python3

description:
  - "This module creates new Elasticsearch clusters in ECE"
  - "supports elasticsearch, Kibana, APM, and ML clusters"

options:
  state:
    description:
      - The desired state for the module
    choices: ['present', 'absent']
    default: present
    type: str
  deployment_name:
    description:
      - Name for the cluster to create or modify
    required: True
    type: str
  elastic_settings:
    description:
      - Settings for Elastic clusters to create
    required: True
    type: list
    suboptions:
      memory_mb:
        description:
          - Amount of memory to assign cluster, in mb
        required: True
        type: int
      instance_config:
        description:
          - Name of the instance configuration to use for the elastic nodes
        required: True
        type: str
      zone_count:
        description:
          - Number of zones to deploy the elasticsearch cluster into
        required: True
        type: int
        choices: [1, 2, 3]
      roles:
        description:
          - Roles the nodes should fufill
        required: True
        type: list
        choices: ['master', 'data', 'ingest']
  version:
    description:
      - Version of the Elastic Stack to deploy
    required: True
    type: str
  deployment_template:
    description:
      - Name of the deployment template to use when deploying the cluster
    required: True
    type: str
  elastic_user_settings:
    description:
      - Settings object to pass as overrides for the elasticsearch.yml file for the cluster
      - Supports all settings definable in elasticsearch.yml
    required: False
    type: dict
  snapshot_settings:
    description:
      - Defines which snapshot repository to use and the retention settings for snapshots
    suboptions:
      repository_name:
        description:
          - Name of the snapshot repository to use for cluster backups
        type: str
        required: True
      snapshots_to_retain:
        description:
          - number of snapshots to retain
        type: int
        default: 100
      snapshot_interval:
        description:
          - How long to wait between snapshots
          - Defined as '60m' for 60 minutes, or '5h' for 5 hours, etc
        type: string
        default: 30m
      enabled:
        description:
          - Whether or not to enable the snapshot repo
        type: bool
        default: true
  kibana_settings:
    description:
      - Settings to apply to the Kibana instances deployed for the elastic cluster
    required: True
    type: dict
    suboptions:
      memory_mb:
        description:
          - Amount of memory to assign to each Kibana instance, in mb
        required: True
        type: int
      instance_config:
        description:
          - instance configuration to use when creating the Kibana instances
        default: kibana
        type: str
      zone_count:
        description:
          - number of zones to deploy Kibana into
        default: 1
        type: int
  apm_settings:
    description:
      - Settings to apply to the Kibana instances deployed for the elastic cluster
    required: True
    type: dict
    suboptions:
      memory_mb:
        description:
          - Amount of memory to assign to each APM instance, in mb
        required: True
        type: int
      instance_config:
        description:
          - instance configuration to use when creating the APM instances
        default: apm
        type: str
      zone_count:
        description:
          - number of zones to deploy Kibana into
        default: 1
        type: int
  ml_settings:
    description:
      - Settings to apply to the Kibana instances deployed for the elastic cluster
    required: False
    type: dict
    suboptions:
      memory_mb:
        description:
          - Amount of memory to assign to each ML instance, in mb
        required: True
        type: int
      instance_config:
        description:
          - instance configuration to use when creating the ML instances
        default: ml
        type: str
      zone_count:
        description:
          - number of zones to deploy Kibana into
        default: 1
        type: int
  logs_and_metric_settings:
    logging_dest: Destination Deployment name for Logging
    metrics_dest: Destination Deployment name for Metrics
    logging_ref_id: Reference ID for Logging
    metrics_ref_id: Reference ID for Metrics
  alias_name: Deployment Alias String
  tag_settings:
  - tag_label: Name of tag
    tag_value: Value of tag 
  wait_for_completion:
    description:
      - Whether to wait for the completion of the cluster operations before exiting the module
      - Impacts how much information is returned at the end of the module run
    default: True
    type: bool
  completion_timeout:
    description:
      - How long to wait, in seconds, for operations to complete before timing out
      - only applies if wait_for_completion is True
    default: 600
    type: int

extends_documentation_fragment:
  - expedient.elastic.ece_auth_options
'''

## need to support both loading as part of a collection and running in test/debug mode
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

import time

from ansible.module_utils.basic import AnsibleModule

def main():
  elastic_settings_spec=dict(
    memory_mb=dict(type='int', required=True),
    instance_config=dict(type='str', default='data.logging'),
    zone_count=dict(type='int', default=2),
    roles=dict(type='list', elements='str', options=['master', 'data', 'ingest']),
  )
  snapshot_settings_spec=dict(
    repository_name=dict(type='str', required=True),
    snapshots_to_retain=dict(type='int', default=100),
    snapshot_interval=dict(type='str', default='60m'),
    enabled=dict(type='bool', default=True),
  )
  kibana_settings_spec=dict(
    memory_mb=dict(type='int', required=True),
    instance_config=dict(type='str', default='kibana'),
    zone_count=dict(type='int', default=1),
  )
  apm_settings_spec=dict(
    memory_mb=dict(type='int', required=True),
    instance_config=dict(type='str', default='apm'),
    zone_count=dict(type='int', default=1),
  )
  ml_settings_spec=dict(
    memory_mb=dict(type='int', required=True),
    instance_config=dict(type='str', default='ml'),
    zone_count=dict(type='int', default=1),
  )
  logs_and_metric_spec=dict(
    logging_dest=dict(type='str', required=True),
    metrics_dest=dict(type='str', required=True),
    logging_ref_id=dict(type='str', default="elasticsearch"),
    metrics_ref_id=dict(type='str', default="elasticsearch")
  )
  tags_spec=dict(
    tag_label=dict(type='str', required=True),
    tag_value=dict(type='str', required=True),
  )
  module_args = dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    no_cluster_object=dict(type='bool', default=True),
    customers_only=dict(type='bool', required=False),
    deployment_name=dict(type='str', required=False),
    elastic_settings=dict(type='list', required=False, elements='dict', options=elastic_settings_spec),
    elastic_user_settings=dict(type='dict', default={}),  # does not have sub-options defined as there are far too many elastic options to capture here
    snapshot_settings=dict(type='dict', required=False, options=snapshot_settings_spec),
    traffic_rulesets=dict(type='list', required=False),
    kibana_settings=dict(type='dict', required=False, options=kibana_settings_spec),
    apm_settings=dict(type='dict', required=False, options=apm_settings_spec),
    ml_settings=dict(type='dict', required=False, options=ml_settings_spec),
    logs_and_metric_settings=dict(type='dict', required=False, options=logs_and_metric_spec),
    alias_name=dict(type='str', required=False),
    tag_settings=dict(type='list', required=False, elements='dict', options=tags_spec),
    version=dict(type='str', default='8.6.0'),
    deployment_template=dict(type='str', required=False),
    wait_for_completion=dict(type='bool', default=False),
    completion_timeout=dict(type='int', default=600),
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
  
  state = module.params.get('state')
  deployment_name = module.params.get('deployment_name')
  version = module.params.get('version')
  elastic_settings = module.params.get('elastic_settings')
  elastic_user_settings = module.params.get('elastic_user_settings')
  snapshot_settings = module.params.get('snapshot_settings')
  traffic_rulesets = module.params.get('traffic_rulesets')
  kibana_settings = module.params.get('kibana_settings')
  apm_settings = module.params.get('apm_settings')
  ml_settings = module.params.get('ml_settings')
  logs_and_metric_settings = module.params.get('logs_and_metric_settings')
  alias_name = module.params.get('alias_name')
  tag_settings = module.params.get('tag_settings')
  deployment_template = module.params.get('deployment_template')
  wait_for_completion = module.params.get('wait_for_completion')
  completion_timeout = module.params.get('completion_timeout')
  
  ece_cluster = ECE(module)
  
  deployment_object = ece_cluster.get_deployment_info(deployment_name)
  #if len(matching_clusters) > 1:
  if deployment_object:
    deployment_name = module.params.get('deployment_name')
    deployment_id = module.params.get('deployment_id')
    no_cluster_object = module.params.get('no_cluster_object')  
    
    ElasticDeployments = ECE(module)
    deployment_objects = []
    deployment_kibana_endpoint = None
    deployment_kibana_http_port = None
    deployment_kibana_https_port = None
    deployment_kibana_url = None
    deployment_kibana_service_url = None
    deployment_elasticsearch_endpoint = None
    deployment_elasticsearch_http_port = None
    deployment_elasticsearch_https_port = None
    deployment_elasticsearch_service_url = None
    deployment_elasticsearch_url = None
    deployment_apm_http_port = None
    deployment_apm_https_port = None
    deployment_apm_service_url = None
    deployment_fleet_service_url = None
    smc_id = None
    
    if deployment_id:
      deployment_objects = [ElasticDeployments.get_deployment_byid(deployment_id)]
    elif deployment_name:
      deployment_objects_results = ElasticDeployments.get_deployment_info(deployment_name)
      if deployment_objects_results != None:
        deployment_objects = [ElasticDeployments.get_deployment_info(deployment_name)]
    else:
      deployment_objects = ElasticDeployments.get_deployment_info()
      deployment_objects = deployment_objects['deployments']
    
    if len(deployment_objects) == 1:
      kibana_info = deployment_objects[0]['resources']['kibana']
      if deployment_objects[0]['resources']['kibana'][0]['info']['status'] != "stopped":
        if 'tags' in deployment_objects[0]['metadata']:
          for tag in deployment_objects[0]['metadata']['tags']:
            if tag['key'] == 'SMC_ID':
              smc_id = tag['value']
        for i in kibana_info:
          if i['ref_id'] == "kibana" or i['ref_id'] == "main-kibana":
            deployment_kibana_endpoint = i['info']['metadata'].get('aliased_endpoint') or i['info']['metadata']['endpoint']
            deployment_kibana_http_port = i['info']['metadata']['ports'].get('http')
            deployment_kibana_https_port = i['info']['metadata']['ports'].get('https')
            deployment_kibana_service_url = i['info']['metadata'].get('service_url')
            deployment_kibana_url = i['info']['metadata'].get('aliased_endpoint')
        elasticsearch_info = deployment_objects[0]['resources']['elasticsearch']
        for i in elasticsearch_info:
          if i['ref_id'] == "elasticsearch" or i['ref_id'] == "main-elasticsearch":
            deployment_elasticsearch_endpoint = i['info']['metadata'].get('aliased_endpoint') or i['info']['metadata']['endpoint']
            deployment_elasticsearch_http_port = i['info']['metadata']['ports'].get('http')
            deployment_elasticsearch_https_port = i['info']['metadata']['ports'].get('https')
            deployment_elasticsearch_service_url = i['info']['metadata'].get('service_url')
            deployment_elasticsearch_url = i['info']['metadata'].get('aliased_endpoint')
            deployment_elasticsearch_version = i['info']['plan_info']['current']['plan']['elasticsearch'].get('version')
        apm_info = deployment_objects[0]['resources']['apm']
        for i in apm_info:
          if i['ref_id'] == "apm" or i['ref_id'] == "main-apm":
            deployment_apm_http_port = i['info']['metadata']['ports'].get('http')
            deployment_apm_https_port = i['info']['metadata']['ports'].get('https')
            if 'services_urls' in i['info']['metadata']:
              for j in i['info']['metadata']['services_urls']:
                if j['service'] == "apm":
                  deployment_apm_service_url = j.get('url')
                if j['service'] == "fleet":
                  deployment_fleet_service_url = j.get('url')
        results['deployment_info'] = {
          "deployment_id": deployment_objects[0]['id'],
          "deployment_name": deployment_objects[0]['name'],
          "resource_type": "kibana",
          "ref_id": deployment_objects[0]['resources']['kibana'][0]['ref_id'],
          "version":  deployment_objects[0]['resources']['kibana'][0]['info']['plan_info']['current']['plan']['kibana']['version']
        }
        results['elastic_deployment_info'] = {
          "deployment_id": deployment_objects[0]['id'],
          "deployment_name": deployment_objects[0]['name'],
          "resource_type": "elasticsearch",
          "ref_id": deployment_objects[0]['resources']['elasticsearch'][0]['ref_id'],
          "version":  deployment_objects[0]['resources']['elasticsearch'][0]['info']['plan_info']['current']['plan']['elasticsearch']['version']
        }
        results['SMC_ID'] = smc_id
        results['deployment_id'] = deployment_objects[0]['id']
        results['deployment_elasticsearch_version'] = deployment_elasticsearch_version
        results['deployment_kibana_endpoint'] = deployment_kibana_endpoint
        results['deployment_kibana_http_port'] = deployment_kibana_http_port
        results['deployment_kibana_https_port'] = deployment_kibana_https_port
        results['deployment_kibana_service_url'] = deployment_kibana_service_url
        results['deployment_kibana_url'] = deployment_kibana_url
        results['deployment_elasticsearch_endpoint'] = deployment_elasticsearch_endpoint
        results['deployment_elasticsearch_http_port'] = deployment_elasticsearch_http_port
        results['deployment_elasticsearch_https_port'] = deployment_elasticsearch_https_port
        results['deployment_elasticsearch_service_url'] = deployment_elasticsearch_service_url
        results['deployment_elasticsearch_url'] = deployment_elasticsearch_url
        results['deployment_apm_http_port'] = deployment_apm_http_port
        results['deployment_apm_https_port'] = deployment_apm_https_port
        results['deployment_apm_service_url'] = deployment_apm_service_url
        results['deployment_fleet_service_url'] = deployment_fleet_service_url
        if no_cluster_object == False:
          results['deployment_object'] = deployment_objects[0]
        else:
          results['deployment_object'] = "No Cluster Object is True by default to reduce output"
        results['deployment_kibana_info'] = "Deployment was returned sucessfully"
      else:
        results['deployment_kibana_info'] = "Unhealthy Deployment Returned"
        results['deployment_kibana_endpoint'] = None
        results['deployment_kibana_http_port'] = None
        results['deployment_kibana_https_port'] = None
        results['deployment_kibana_url'] = None
        results['deployment_kibana_service_url'] = None
        results['deployment_elasticsearch_url'] = None
        results['deployment_elasticsearch_service_url'] = None
        results['deployment_apm_service_url'] = None
        results['deployment_fleet_service_url'] = None
        results['deployment_objects'] = deployment_objects
    elif len(deployment_objects) == 0:
      results['deployment_kibana_info'] = "No deployment was returned, check your deployment name"
      results['deployment_kibana_endpoint'] = None
      results['deployment_kibana_http_port'] = None
      results['deployment_kibana_https_port'] = None
      results['deployment_kibana_url'] = None
      results['deployment_kibana_service_url'] = None
      results['deployment_elasticsearch_url'] = None
      results['deployment_elasticsearch_service_url'] = None
      results['deployment_apm_service_url'] = None
      results['deployment_fleet_service_url'] = None
    else:
      results['deployment_objects'] = deployment_objects

  if state == 'present':
    #if len(matching_clusters) > 0:
    if deployment_object and (elastic_settings or kibana_settings or apm_settings):
      results['msg'] = 'cluster exists'
      results['cluster_data'] = {
        'elasticsearch_cluster_id': deployment_object['resources']['elasticsearch'][0]['id'],
        'kibana_cluster_id': deployment_object['resources']['kibana'][0]['id']
      }
      if len( deployment_object['resources']['apm']) > 0:
        results['cluster_data']['apm_id'] = deployment_object['resources']['apm'][0]['id']
      module.exit_json(**results)

    results['changed'] = True
    results['msg'] = f'cluster {module.params.get("deployment_name")} will be created and/or updated'
    if not module.check_mode and (elastic_settings or kibana_settings or apm_settings):
      cluster_data = ece_cluster.create_cluster(
          deployment_name,
          version,
          deployment_template, 
          elastic_settings, 
          kibana_settings, 
          elastic_user_settings, 
          apm_settings, 
          ml_settings, 
          snapshot_settings,
          traffic_rulesets,
          wait_for_completion,
          completion_timeout
          )
      if not cluster_data:
        results['msg'] = 'cluster creation failed'
        module.fail_json(**results)
      results['cluster_data'] = cluster_data
      deployment_healthy = ece_cluster.wait_for_cluster_healthy(cluster_data['id'])
      if deployment_healthy == False:
        results['cluster_data']['msg'] = "Cluster information may be incomplete because the cluster is not healthy"
      else:
        time.sleep(30)
      deployment_object = ece_cluster.get_deployment_byid(cluster_data['id'])
      for resource in cluster_data['resources']:
        if resource['kind'] == "elasticsearch":
          results['cluster_data']['credentials'] = resource['credentials']
          continue
      for kind_object_name in deployment_object['resources']:
        for kind_object in deployment_object['resources'][kind_object_name]:
          if 'cluster_id' in kind_object['info']:
            results['cluster_data'][kind_object_name + '_cluster_id'] = kind_object['info']['cluster_id']
          elif 'deployment_id' in kind_object['info']:
            results['cluster_data'][kind_object_name + '_cluster_id'] = kind_object['info']['deployment_id']
          if 'services_urls' in kind_object['info']['metadata']:
            for service_url in kind_object['info']['metadata']['services_urls']:
              results['cluster_data'][service_url['service'] + '_cluster_url'] = service_url['url']
          elif 'service_url' in kind_object['info']['metadata']:
            results['cluster_data'][kind_object_name + '_cluster_url'] = kind_object['info']['metadata']['service_url']
      results['msg'] = f'cluster {module.params.get("deployment_name")} created'
    
    update_body  = {}
    
    if logs_and_metric_settings:
      
      logging_object = [ece_cluster.get_deployment_info(logs_and_metric_settings['logging_dest'])]
      metrics_object = [ece_cluster.get_deployment_info(logs_and_metric_settings['metrics_dest'])]
      logging_ref_id = logs_and_metric_settings['logging_ref_id']
      metrics_ref_id = logs_and_metric_settings['metrics_ref_id']
      
      if deployment_object:
        logs_update_body = {
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
            'observability': logs_update_body
          },
          'prune_orphans': False
        }
        update_body.update(body)

    if tag_settings:
      tag_list = []
      
      if 'tags' in deployment_object['metadata']:
        for tag in deployment_object['metadata']['tags']:
          tag_list.append(tag)
          
      for each_tag in tag_settings:
        if 'tag_label' in each_tag and 'tag_value' in each_tag:
          tag_body = {
            "key": each_tag['tag_label'],
            "value": each_tag['tag_value']
          }
          tag_list.append(tag_body)

      tag_list_next = tag_list

      for each_orig_tag in tag_list:
        match = 0
        for each_updated_tag in tag_list_next:
          if each_updated_tag['key'] == each_orig_tag['key']:
            match = match + 1
            if match > 1:
              tag_list.remove(each_updated_tag)

      tag_update_body = {
        "metadata": {
          "tags": tag_list
        },
        "prune_orphans": False
      }

      update_body.update(tag_update_body)
          
    if alias_name:
      
      if alias_name == 'default':
        if tag_update_body:
          tag_body = tag_update_body
        else: 
          tag_body = deployment_object
        if tag_body:
          for tag in tag_body['metadata']['tags']:
            if tag['key'] == "SMC_ID":
              SMC_ID = tag['value']
        if alias_name == 'default':
          alias_name = 'elastic-' + deployment_object['id'] + '-' + SMC_ID

      alias_update_body = {
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
        }
      }
      update_body.update(alias_update_body)
    
    if update_body:
      
      ece_cluster.update_deployment_byid(deployment_object['id'], update_body)
      ece_cluster.wait_for_cluster_state(deployment_object['id'], "elasticsearch" ) # Wait for ElasticSearch
      ece_cluster.wait_for_cluster_state(deployment_object['id'], "kibana" ) # Wait for Kibana
      deployment_healthy = ece_cluster.wait_for_cluster_state(deployment_object['id'], "kibana","main-apm") # If APM is healthy then the deployment is healthy since apm is last to come up

      if deployment_healthy == False:
        results['cluster_alias_status'] = "Cluster information may be incomplete because the cluster is not healthy"
      else:
        time.sleep(30)
        
    module.exit_json(**results)

  if state == 'absent':
    if len(deployment_object) == 0:
      results['msg'] = f'cluster {module.params.get("deployment_name")} does not exist'
      module.exit_json(**results)

    results['msg'] = f'cluster {module.params.get("deployment_name")} will be deleted'
    if not module.check_mode:
      results['changed'] = True
      ece_cluster.delete_cluster(deployment_object['id'])
      results['msg'] = f'cluster {module.params.get("deployment_name")} deleted'
      module.exit_json(**results)

if __name__ == '__main__':
  main()
