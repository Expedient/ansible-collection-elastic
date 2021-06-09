#!/usr/bin/python
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
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ansible.module_utils.basic import AnsibleModule


class ECE_Cluster(ECE):
  def __init__(self, module):
    super().__init__(module)
    self.cluster_name = self.module.params.get('cluster_name')
    self.elastic_settings = self.module.params.get('elastic_settings')
    self.kibana_settings = self.module.params.get('kibana_settings')
    self.apm_settings = self.module.params.get('apm_settings')
    self.ml_settings = self.module.params.get('ml_settings')
    self.version = self.module.params.get('version')
    self.deployment_template = self.module.params.get('deployment_template')
    self.wait_for_completion = self.module.params.get('wait_for_completion')
    self.completion_timeout = self.module.params.get('completion_timeout')
    self.elastic_user_settings = self.module.params.get('elastic_user_settings')
    self.snapshot_settings = self.module.params.get('snapshot_settings')
    self.traffic_rulesets = self.module.params.get('traffic_rulesets')



  def get_matching_clusters(self):
    clusters = self.get_clusters_by_name(self.cluster_name)
    return clusters

  def create_cluster(self):
    data = {
      'cluster_name': self.cluster_name,
      'plan': {
        'cluster_topology': [{
          'size': {
            'value': settings['memory_mb'],
            'resource': 'memory'
          },
          'node_type': {
            'master': 'master' in settings['roles'],
            'data': 'data' in settings['roles'],
            'ingest': 'ingest' in settings['roles']
          },
          'instance_configuration_id': self.get_instance_config(settings['instance_config'])['id'],
          'elasticsearch': {
            'enabled_built_in_plugins': [],
            'node_attributes': {},
            'user_settings_yaml': dump(self.elastic_user_settings, Dumper=Dumper),
          },
          'zone_count': settings['zone_count']
        } for settings in self.elastic_settings],
        'elasticsearch': {
          'version': self.version
        },
        'transient': {},
        'deployment_template': {
          'id': self.get_deployment_template(self.deployment_template)['id']
        },
      },
      'settings': {},
      'kibana': {
        'plan': {
          'cluster_topology': [{
            'instance_configuration_id': self.get_instance_config(self.kibana_settings['instance_config'])['id'],
            'size': {
              'value': self.kibana_settings['memory_mb'],
              'resource': 'memory'
            },
            'zone_count': self.kibana_settings['zone_count']
          }],
          'kibana': {
            ## using a default value here, if we want to extend it later it can be
            'user_settings_yaml': "# Note that the syntax for user settings can change between major versions.\n# You might need to update these user settings before performing a major version upgrade.\n#\n# Use OpenStreetMap for tiles:\n# tilemap:\n#   options.maxZoom: 18\n#   url: http://a.tile.openstreetmap.org/{z}/{x}/{y}.png\n#\n# To learn more, see the documentation.",
            'version': self.version
          }
        },
      }
    }

    if self.apm_settings:
      data['apm'] = {
        'plan': {
          'cluster_topology': [{
              'instance_configuration_id': self.get_instance_config(self.apm_settings['instance_config'])['id'],
              'size': {
                'value': self.apm_settings['memory_mb'],
                'resource': 'memory'
              },
              'zone_count': self.apm_settings['zone_count']
            }],
            'apm': {'version': self.version}
        }
      }

    ## This is technically just another ES deployment rather than it's own config, but decided to follow the UI rather than API conventions
    if self.ml_settings:
      data['plan']['cluster_topology'].append({
                  'instance_configuration_id': self.get_instance_config(self.ml_settings['instance_config'])['id'],
                  'size': {
                    'value': self.ml_settings['memory_mb'],
                    'resource': 'memory'
                  },
                  'node_type': {
                    'master': False,
                    'data': False,
                    'ingest': False,
                    'ml': True
                  },
                  'zone_count': self.ml_settings['zone_count']
                })

    if self.snapshot_settings:
      data['settings']['snapshot'] = {
        'repository': {
          'reference': {
            'repository_name': self.snapshot_settings['repository_name']
          }
        },
        'enabled': self.snapshot_settings['enabled'],
        'retention': {
          'snapshots': self.snapshot_settings['snapshots_to_retain'],
        },
        'interval': self.snapshot_settings['snapshot_interval']
      }

    if self.traffic_rulesets:
      data['settings']['ip_filtering'] = {
        'rulesets': [self.get_traffic_ruleset_by_name(x)['id'] for x in self.traffic_rulesets]
      }

    endpoint = 'clusters/elasticsearch'
    cluster_creation_result = self.send_api_request(endpoint, 'POST', data=data)
    if self.wait_for_completion:
      elastic_result = self.wait_for_cluster_state('elasticsearch', cluster_creation_result['elasticsearch_cluster_id'], 'started', self.completion_timeout)
      kibana_result = self.wait_for_cluster_state('kibana', cluster_creation_result['kibana_cluster_id'], 'started', self.completion_timeout)
      if not elastic_result and kibana_result:
        return False
    cluster = self.get_cluster_by_id('elasticsearch', cluster_creation_result['elasticsearch_cluster_id'])
    return cluster

  def delete_cluster(self, cluster_id):
    self.terminate_cluster(cluster_id)
    endpoint = f'clusters/elasticsearch/{cluster_id}'
    delete_result = self.send_api_request(endpoint, 'DELETE')
    return delete_result

  def terminate_cluster(self, cluster_id):
    endpoint = f'clusters/elasticsearch/{cluster_id}/_shutdown'
    stop_result = self.send_api_request(endpoint, 'POST')
    wait_result = self.wait_for_cluster_state('elasticsearch', cluster_id, 'stopped', self.completion_timeout)
    if not wait_result:
      self.module.fail_json(msg=f'failed to stop cluster {self.cluster_name}')
    return stop_result



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
    version=dict(type='str', default='7.7.0'),
    deployment_template=dict(type='str', required=False),
    wait_for_completion=dict(type='bool', default=False),
    completion_timeout=dict(type='int', default=10),
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
  state = module.params.get('state')
  ece_cluster = ECE_Cluster(module)

  matching_clusters = ece_cluster.get_matching_clusters()
  if len(matching_clusters) > 1:
    results['msg'] = f'found multiple clusters matching name {module.params.get("cluster_name")}'
    module.fail_json(**results)

  if state == 'present':
    if len(matching_clusters) == 1:
      results['msg'] = 'cluster exists'
      module.exit_json(**results)

    results['changed'] = True
    results['msg'] = f'cluster {module.params.get("cluster_name")} will be created'
    if not module.check_mode:
      cluster_data = ece_cluster.create_cluster()
      if not cluster_data:
        results['msg'] = 'cluster creation failed'
        module.fail_json(**results)
      results['cluster_data'] = cluster_data
      results['msg'] = f'cluster {module.params.get("cluster_name")} created'
    module.exit_json(**results)

  if state == 'absent':
    if len(matching_clusters) == 0:
      results['msg'] = f'cluster {module.params.get("cluster_name")} does not exist'
      module.exit_json(**results)

    results['msg'] = f'cluster {module.params.get("cluster_name")} will be deleted'
    if not module.check_mode:
      results['changed'] = True
      ece_cluster.delete_cluster(matching_clusters[0]['cluster_id'])
      results['msg'] = f'cluster {module.params.get("cluster_name")} deleted'
      module.exit_json(**results)





if __name__ == '__main__':
  main()