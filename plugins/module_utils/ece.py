# Copyright 2021 mike.garuccio
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

from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
import time
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ECE(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')

    if self.username and self.password:
      url = f'https://{self.host}:{self.port}/api/v1/users/auth/_login'
      data = {
        'username': self.username,
        'password': self.password
      }
      payload = dumps(data)
      headers = {'Content-Type': 'application/json'}
      response = open_url(url, data=payload, headers=headers, method='POST', validate_certs=self.validate_certs)
      content = loads(response.read())
      self.token = content['token']

  def send_api_request(self, endpoint, method, data=None):
    url = f'https://{self.host}:{self.port}/api/v1/{endpoint}'
    headers = {'Authorization': f'Bearer {self.token}'}
    payload = None
    if data:
      payload = dumps(data)
      headers['Content-Type'] = 'application/json'
    response = open_url(url, data=payload, headers=headers, method=method, validate_certs=self.validate_certs)
    content = loads(response.read())
    return content

  def get_deployment_info(self, deployment_name = None):
    endpoint  = 'deployments'
    all_deployment_objects = self.send_api_request(endpoint, 'GET')
    deployment_objects = None
    if deployment_name:
      for deployment in all_deployment_objects['deployments']:
        if str(deployment['name']).upper() == str(deployment_name).upper():
          endpoint  = 'deployments/' + deployment['id']
          deployment_objects = self.send_api_request(endpoint, 'GET')
          break
    else:
      deployment_objects = all_deployment_objects
    return deployment_objects

  def get_deployment_byid(self, deployment_id):
    endpoint  = f'deployments/{deployment_id}'
    deployment_object = self.send_api_request(endpoint, 'GET')
    return deployment_object

  def get_clusters(self):
    #endpoint = 'clusters/elasticsearch'
    #endpoint = f'deployments'
    #clusters = self.send_api_request(endpoint, 'GET')
    deployment_objects = self.get_deployment_info()
    return deployment_objects['deployments']

  ## This is a bad implementation and should probably be removed
  ## see below `get_cluster_by_name()` function for current implementation
  def get_clusters_by_name(self, deployment_name):
    #endpoint = f'clusters/elasticsearch?q=cluster_name={cluster_name}'
    #clusters = self.send_api_request(endpoint, 'GET')
    deployment_object = self.get_deployment_info(deployment_name)
    return deployment_object
  
  def get_deployment_resource_by_id(self, cluster_id, resource_kind, ref_id):
    endpoint = f'deployments/{cluster_id}/{resource_kind}/{ref_id}'
    deployment_resource = self.send_api_request(endpoint, 'GET')
    return deployment_resource

  def get_deployment_resource_by_kind(self, deployment_id, resource_kind):
    deployment_info = self.get_cluster_by_id(deployment_id)
    ########## It is possible to have multiple resources of the same kind, but for now the first will be taken
    ##########    This is highly like to be the main resource.
    return deployment_info['resources'][resource_kind][0]
  
  ## Applying the additional Python filter removes issues with a partial name match
  def get_cluster_by_name(self, cluster_name, resource_kind = "elasticsearch"):
    #endpoint = f'clusters/elasticsearch?q=cluster_name={cluster_name}'
    #clusters = self.send_api_request(endpoint, 'GET')
    #return next(filter(lambda x: x['cluster_name'] == cluster_name, clusters['elasticsearch_clusters']), None)
    clusters = self.get_clusters()
    target_cluster = None
    target_cluster_resource = None
    for cluster in clusters:
      if cluster['name'] == cluster_name:
        target_cluster = cluster
        for resource in cluster['resources'][resource_kind]:
          if resource['kind'] == resource_kind:
            target_cluster_resource = self.get_cluster_resource_by_id(target_cluster['id'],resource_kind, resource['ref_id'])
            break
    return target_cluster_resource

  def get_cluster_by_id(self, cluster_id):
    #endpoint = f'clusters/{cluster_type}/{cluster_id}'
    endpoint = f'deployments/{cluster_id}'
    cluster = self.send_api_request(endpoint, 'GET')
    return cluster

  def get_instance_config(self, config_name):
    endpoint = 'platform/configuration/instances'
    instances = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == config_name, instances), None)

  def get_deployment_template(self, template_name):
    #endpoint = 'platform/configuration/templates/deployments'
    endpoint = 'deployments/templates?region=ece-region'
    templates = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == template_name, templates), None)

  def wait_for_cluster_state(self, cluster_id, resource_kind, resource_ref_id = None, cluster_state = 'started', completion_timeout=600):
    if resource_ref_id == None:
      resource_ref_id = f"main-{resource_kind}"
    timeout = time.time() + completion_timeout
    cluster_object = self.get_cluster_by_id(cluster_id)
    x = 0
    for resource in cluster_object['resources'][resource_kind]:
      if resource['ref_id'] == resource_ref_id:
        while cluster_object['resources'][resource_kind][x]['info']['status'] != cluster_state:
          time.sleep(1)
          if time.time() > timeout:
            return False
          cluster_object = self.get_cluster_by_id(cluster_id)
      x = x + 1
    return True

  def get_traffic_rulesets(self, include_assocations=False):
    endpoint = 'deployments/traffic-filter/rulesets'
    if include_assocations:
      endpoint = f'{endpoint}?include_associations=true'
    response = self.send_api_request(endpoint, 'GET')
    return response['rulesets']

  def get_traffic_ruleset_by_name(self, rule_name, include_assocations=False):
    rules = self.get_traffic_rulesets(include_assocations=include_assocations)
    return next(filter(lambda x: x['name'] == rule_name, rules), None)

  def get_snapshot_repos(self):
    endpoint = 'platform/configuration/snapshots/repositories'
    response = self.send_api_request(endpoint, 'GET')
    return response['configs']

  def get_snapshot_repo_by_name(self, repo_name):
    repos = self.get_snapshot_repos()
    return next(filter(lambda x: x['repository_name'] == repo_name, repos), None)

  def get_deployment_kibana_info(self,deployment_name):
    deployment_object = self.get_deployment_info(deployment_name)
    deployment_resource = self.get_deployment_resource_by_kind(deployment_object['id'], "kibana")
    return deployment_resource

  def update_deployment_info(self, deployment_name, config):
    deployment_objects = self.get_deployment_info()
    target_deployment_object = ""
    for deployment in deployment_objects['deployments']:
      if str(deployment['name']).upper() == str(deployment_name).upper():
        endpoint  = 'deployments/' + deployment['id']
        target_deployment_object = self.send_api_request(endpoint, 'PUT', config)
        break
    return target_deployment_object

  def create_cluster(self, 
                     cluster_name, 
                     version, 
                     deployment_template, 
                     elastic_settings, 
                     kibana_settings, 
                     elastic_user_settings, 
                     apm_settings, 
                     ml_settings = None, 
                     snapshot_settings = None, 
                     traffic_rulesets = None,
                     wait_for_completion = False,
                     completion_timeout = 600
                     ):
      x = 0
      for role in elastic_settings[0]['roles']:
        if role == 'data':
          elastic_settings[0]['roles'][x] = 'data_hot'
        x = x + 1
      elastic_settings[0]['roles'].append('data_content')
      deployment_template_object = self.get_deployment_template(deployment_template)
      data = {
        'name': cluster_name,
        'settings': {},
        'resources': {
          'elasticsearch': [
            {
              'ref_id': 'main-elasticsearch',
              'region': 'ece-region',
              'plan': {
                'deployment_template': {
                  'id': deployment_template_object['id']
                },
                'elasticsearch': {
                    'version': version
                },
                'cluster_topology': [
                  {
                    'id': 'hot_content',
                    'node_roles': elastic_settings[0]['roles'],
                    'zone_count': elastic_settings[0]['zone_count'],
                    'elasticsearch': {
                      'enabled_built_in_plugins': [],
                      'node_attributes': {},
                      'user_settings_yaml': dump(elastic_user_settings, Dumper=Dumper),
                    },
                    'size': {
                      'value': elastic_settings[0]['memory_mb'],
                      'resource': 'memory'
                    },
                    'instance_configuration_id': self.get_instance_config(elastic_settings[0]['instance_config'])['id']
                  },
                ]
              }
            }
          ]
        }
      }
      if kibana_settings:
        kibana_data = {
          'ref_id': 'main-kibana',
          'elasticsearch_cluster_ref_id': 'main-elasticsearch',
          'region': 'ece-region',
          'plan': {
            'cluster_topology': [{
              'instance_configuration_id': self.get_instance_config(kibana_settings['instance_config'])['id'],
              'size': {
                'value': kibana_settings['memory_mb'],
                'resource': 'memory'
              },
              'zone_count': kibana_settings['zone_count']
            }],
            'kibana': {
              'user_settings_yaml': '# Note that the syntax for user settings can change between major versions.\n# You might need to update these user settings before performing a major version upgrade.\n#\n# Use OpenStreetMap for tiles:\n# tilemap:\n#   options.maxZoom: 18\n#   url: http://a.tile.openstreetmap.org/{z}/{x}/{y}.png\n#\n# To learn more, see the documentation.',
              'version': version
            }
          }
        }
        data['resources']['kibana'] = []
        data['resources']['kibana'].append(kibana_data)


      if apm_settings:
        apm_data = {
          'ref_id': 'main-apm',
          'region': 'ece-region',
          'elasticsearch_cluster_ref_id': 'main-elasticsearch',
          'plan': {
            'cluster_topology': [{
                'instance_configuration_id': self.get_instance_config(apm_settings['instance_config'])['id'],
                'size': {
                  'value': apm_settings['memory_mb'],
                  'resource': 'memory'
                },
                'zone_count': apm_settings['zone_count']
              }],
              'apm': {'version': version}
          }
        }
        data['resources']['apm'] = []
        data['resources']['apm'].append(apm_data)

      ## This is technically just another ES deployment rather than it's own config, but decided to follow the UI rather than API conventions
      if ml_settings:
        ml_data = {
          'id': "ml",
          'instance_configuration_id': "ml",
          'size': {
            'value': ml_settings['memory_mb'],
            'resource': 'memory'
          },
          'node_roles': ['ml', 'remote_cluster_client'],
          'zone_count': ml_settings['zone_count']
        }
        x = 0
        for resource in data['resources']['elasticsearch']:
          if resource['ref_id'] == "main-elasticsearch":
            data['resources']['elasticsearch'][x]['plan']['cluster_topology'].append(ml_data)
          x = x + 1

      if snapshot_settings:
        #data['settings']['snapshot'] = {
        snapshot_settings = {
          'repository': {
            'reference': {
              'repository_name': snapshot_settings['repository_name']
            }
          },
          'enabled': snapshot_settings['enabled'],
          'retention': {
            'snapshots': snapshot_settings['snapshots_to_retain'],
          },
          'interval': snapshot_settings['snapshot_interval']
        }
        x = 0
        for resource in data['resources']['elasticsearch']:
          if resource['ref_id'] == "main-elasticsearch":
            if not 'settings' in data['resources']['elasticsearch'][x]:
              data['resources']['elasticsearch'][x]['settings'] = {}
            data['resources']['elasticsearch'][x]['settings']['snapshot'] = snapshot_settings
          x = x + 1

      if traffic_rulesets:
        ip_filtering_data = {
          'rulesets': [self.get_traffic_ruleset_by_name(x)['id'] for x in self.traffic_rulesets]
        }

      endpoint = 'deployments'
      cluster_creation_result = self.send_api_request(endpoint, 'POST', data=data)
      if wait_for_completion:
        elastic_deployment_result = self. wait_for_cluster_state(cluster_creation_result['id'],'elasticsearch','main-elasticsearch','started', completion_timeout)
        kibana_deployment_result = self.wait_for_cluster_state(cluster_creation_result['id'],'kibana','main-kibana','started', completion_timeout)
        if not elastic_deployment_result and not kibana_deployment_result:
          return False
      return cluster_creation_result

  def get_matching_clusters(self, cluster_name):
    clusters = self.get_clusters_by_name(cluster_name)
    return clusters

  def delete_cluster(self, deployment_id):
    self.terminate_cluster(deployment_id)
    #endpoint = f'clusters/elasticsearch/{cluster_id}'
    #target_resource_object = self.get_deployment_resource_by_kind(deployment_id, resource_kind)
    #target_resource_ref_id = target_resource_object['ref_id']
    #endpoint = f'deployments/{deployment_id}/{resource_kind}/{target_resource_ref_id}'
    endpoint = f'deployments/{deployment_id}'
    delete_result = self.send_api_request(endpoint, 'DELETE')
    return delete_result

  def terminate_cluster(self, deployment_id, resource_kind = "elasticsearch"):
    #endpoint = f'clusters/elasticsearch/{cluster_id}/_shutdown'
    target_deployment_object = self.get_deployment_byid(deployment_id)
    resources = target_deployment_object['resources'][resource_kind]
    for resource in resources: 
      target_resource_ref_id = resource['ref_id']
      endpoint = f'deployments/{deployment_id}/{resource_kind}/{target_resource_ref_id}/_shutdown'
      stop_result = self.send_api_request(endpoint, 'POST')
      wait_result = self.wait_for_cluster_state(deployment_id, resource_kind, target_resource_ref_id,'stopped', self.completion_timeout)
    if not wait_result:
      self.module.fail_json(msg=f'failed to stop deployment {deployment_id}')
    return stop_result

  def set_elastic_user_password(self, deployment_id, resource_kind = "elasticsearch", ref_id = "main-elasticsearch"):
    endpoint = f'deployments/{deployment_id}/{resource_kind}/{ref_id}/_reset-password'
    credentail_object = self.send_api_request(endpoint, 'POST')
    return credentail_object