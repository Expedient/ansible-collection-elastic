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
  cluster_name:
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

  module_args = dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    cluster_name=dict(type='str', required=True),
    elastic_settings=dict(type='list', required=False, elements='dict', options=elastic_settings_spec),
    elastic_user_settings=dict(type='dict', default={}),  # does not have sub-options defined as there are far too many elastic options to capture here
    snapshot_settings=dict(type='dict', required=False, options=snapshot_settings_spec),
    traffic_rulesets=dict(type='list', required=False),
    kibana_settings=dict(type='dict', required=False, options=kibana_settings_spec),
    apm_settings=dict(type='dict', required=False, options=apm_settings_spec),
    ml_settings=dict(type='dict', required=False, options=ml_settings_spec),
    version=dict(type='str', default='8.3.3'),
    deployment_template=dict(type='str', required=True),
    wait_for_completion=dict(type='bool', default=False),
    completion_timeout=dict(type='int', default=600),
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
  
  state = module.params.get('state')
  cluster_name = module.params.get('cluster_name')
  version = module.params.get('version')
  elastic_settings = module.params.get('elastic_settings')
  elastic_user_settings = module.params.get('elastic_user_settings')
  snapshot_settings = module.params.get('snapshot_settings')
  traffic_rulesets = module.params.get('traffic_rulesets')
  kibana_settings = module.params.get('kibana_settings')
  apm_settings = module.params.get('apm_settings')
  ml_settings = module.params.get('ml_settings')
  deployment_template = module.params.get('deployment_template')
  wait_for_completion = module.params.get('wait_for_completion')
  completion_timeout = module.params.get('completion_timeout')
  
  ece_cluster = ECE(module)
  

  matching_clusters = ece_cluster.get_matching_clusters(cluster_name)
  #if len(matching_clusters) > 1:
  if matching_clusters:
    #results['msg'] = f'found multiple clusters matching name {module.params.get("cluster_name")}'
    results['msg'] = f'found cluster matching name {module.params.get("cluster_name")}'
    #module.fail_json(**results)

  if state == 'present':
    #if len(matching_clusters) > 0:
    if matching_clusters:
      results['msg'] = 'cluster exists'
      ## This code handles edge cases poorly, in the interest of being able to match the data format of the cluster creation result
      results['cluster_data'] = {
        'elasticsearch_cluster_id': matching_clusters['resources']['elasticsearch'][0]['id'],
        'kibana_cluster_id': matching_clusters['resources']['kibana'][0]['id']
      }
      if len( matching_clusters['resources']['apm']) > 0:
        results['cluster_data']['apm_id'] = matching_clusters['resources']['apm'][0]['id']
      module.exit_json(**results)

    results['changed'] = True
    results['msg'] = f'cluster {module.params.get("cluster_name")} will be created'
    if not module.check_mode:
      cluster_data = ece_cluster.create_cluster(
          cluster_name,
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
      for resource in cluster_data['resources']:
        if resource['ref_id'] == "main-elasticsearch":
          elasticsearch_cluster_id = resource['id']
          elasticsearch_credentials = resource['credentials']
        if resource['ref_id'] == "main-kibana":
          kibana_cluster_id = resource['id']
      results['cluster_data']['elasticsearch_cluster_id'] = elasticsearch_cluster_id
      results['cluster_data']['kibana_cluster_id'] = kibana_cluster_id
      results['cluster_data']['credentials'] = elasticsearch_credentials
      results['msg'] = f'cluster {module.params.get("cluster_name")} created'
    module.exit_json(**results)

  if state == 'absent':
    if len(matching_clusters) == 0:
      results['msg'] = f'cluster {module.params.get("cluster_name")} does not exist'
      module.exit_json(**results)

    results['msg'] = f'cluster {module.params.get("cluster_name")} will be deleted'
    if not module.check_mode:
      results['changed'] = True
      ece_cluster.delete_cluster(matching_clusters['id'])
      results['msg'] = f'cluster {module.params.get("cluster_name")} deleted'
      module.exit_json(**results)

if __name__ == '__main__':
  main()
