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

  def get_clusters(self):
    endpoint = 'clusters/elasticsearch'
    clusters = self.send_api_request(endpoint, 'GET')
    return clusters['elasticsearch_clusters']

  ## This is a bad implementation and should probably be removed
  ## see below `get_cluster_by_name()` function for current implementation
  def get_clusters_by_name(self, cluster_name):
    endpoint = f'clusters/elasticsearch?q=cluster_name={cluster_name}'
    clusters = self.send_api_request(endpoint, 'GET')
    return clusters['elasticsearch_clusters']

  ## Applying the additional Python filter removes issues with a partial name match
  def get_cluster_by_name(self, cluster_name):
    endpoint = f'clusters/elasticsearch?q=cluster_name={cluster_name}'
    clusters = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['cluster_name'] == cluster_name, clusters['elasticsearch_clusters']), None)

  def get_cluster_by_id(self, cluster_type, cluster_id):
    endpoint = f'clusters/{cluster_type}/{cluster_id}'
    cluster = self.send_api_request(endpoint, 'GET')
    return cluster

  def get_instance_config(self, config_name):
    endpoint = 'platform/configuration/instances'
    instances = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == config_name, instances), None)

  def get_deployment_template(self, template_name):
    endpoint = 'platform/configuration/templates/deployments'
    templates = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == template_name, templates), None)

  def wait_for_cluster_state(self, cluster_type, cluster_id, cluster_state, completion_timeout=600):
    timeout = time.time() + completion_timeout
    while self.get_cluster_by_id(cluster_type, cluster_id)['status'] != cluster_state:
      time.sleep(1)
      if time.time() > timeout:
        return False
    return True

  def get_traffic_rulesets(self, include_assocations=False):
    endpoint = 'deployments/ip-filtering/rulesets'
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
      deployment_object = None
      endpoint  = 'deployments'
      deployment_objects = self.send_api_request(endpoint, 'GET')
      for deployment in deployment_objects['deployments']:
        if str(deployment['name']).upper() == str(deployment_name).upper():
          for resources in deployment['resources']:
              if resources['kind'] == "kibana":
                resource_name = resources['ref_id']
                endpoint  = 'deployments/' + deployment['id'] + '/kibana/' + resource_name
                deployment_object = self.send_api_request(endpoint, 'GET')
          break
      return deployment_object

  def get_deployment_info(self, deployment_name):
      deployment_object = None
      endpoint  = 'deployments'
      deployment_objects = self.send_api_request(endpoint, 'GET')
      deployment_object = ""
      for deployment in deployment_objects['deployments']:
        if str(deployment['name']).upper() == str(deployment_name).upper():
          endpoint  = 'deployments/' + deployment['id']
          deployment_object = self.send_api_request(endpoint, 'GET')
          break
      return deployment_object

  def update_deployment_info(self, deployment_name, config):
      deployment_object = None
      endpoint  = 'deployments'
      deployment_objects = self.send_api_request(endpoint, 'GET')
      deployment_object = ""
      for deployment in deployment_objects['deployments']:
        if str(deployment['name']).upper() == str(deployment_name).upper():
          endpoint  = 'deployments/' + deployment['id']
          deployment_object = self.send_api_request(endpoint, 'PUT', config)
          break
      return deployment_object