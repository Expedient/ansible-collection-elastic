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

from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
from urllib.error import HTTPError
import urllib.parse


class Kibana(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.version = None # this is a hack to make it so that we can run the first request to get the clutser version without erroring out
    self.version = self.get_cluster_version()

  def send_api_request(self, endpoint, method, data=None):
    url = f'https://{self.host}:{self.port}/api/{endpoint}'
    headers = {}
    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    if self.version:
      headers['kbn-version'] = self.version
    try:
      response = open_url(url, data=payload, method=method, validate_certs=self.validate_certs, headers=headers,
                          force_basic_auth=True, url_username=self.username, url_password=self.password, timeout=60)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.read())

  def get_cluster_status(self):
    endpoint = 'status'
    return self.send_api_request(endpoint, 'GET')

  def get_cluster_version(self):
    status = self.get_cluster_status()
    return status['version']['number']

  def get_alert_types(self):
    endpoint = 'alert/types'
    alert_types = self.send_api_request(endpoint, 'GET')
    return alert_types

  def get_alert_by_name(self, alert_name):
    endpoint = f'alerts/_find?search_fields=name&search={urllib.parse.quote(alert_name)}'
    alerts = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == alert_name, alerts['data']), None)

  def get_alert_connector_by_name(self, connector_name):
    endpoint = 'actions/connectors'
    actions = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == connector_name, actions), None)

  def get_alert_connector_type_by_name(self, connector_type_name):
    endpoint = 'actions/connector_types'
    connector_types = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == connector_type_name, connector_types), None)
  
  # Elastic Rules functions

  def update_rule(self, body):
    endpoint = "detection_engine/rules"
    update_rule = self.send_api_request(endpoint,'PATCH',data=body)
    return update_rule

  def get_rules(self,page_size,page_no):
    endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size)
    rules = self.send_api_request(endpoint, 'GET')
    return rules
  
  def enable_rule(self,rule_id):
    body={
      'enabled': True,
      'id': rule_id
    }
    update_rule = self.update_rule(self, body)
    return update_rule

  def activating_all_rules(self, page_size):
    #### Getting first page of rules
    page_number = 1
    rules = self.get_rules(self,page_size,page_number)
    noOfRules = rules['total']
    allrules = rules['data']
    #### Going through each rule page by page and enabling each rule that isn't enabled.
    while noOfRules > page_size * (page_number - 1):
        for rule in allrules:
          if rule['enabled'] == False:
            enable_rule = self.enable_rule(self,rule['id'])
            return(rule['id'] + ": Rule is updated")
        page_number = page_number + 1
        rules = self.get_rules(self,page_size,page_number)
        allrules = rules['data']
    return "Rules are updated"

  def activate_rule(self, page_size, rule_name = 'All'):

    #### Getting first page of rules
    page_number = 1
    rules = self.get_rules(page_size,page_number)
    noOfRules = rules['total']
    allrules = rules['data']
    #### Going through each rule page by page and enabling each rule that isn't enabled.
    while noOfRules > page_size * (page_number - 1):
        for rule in allrules:
          if rule['enabled'] == False and rule_name == rule['name']:
            enable_rule = self.enable_rule(self,rule['id'])
            return(rule['name'] + ": Rule is updated")
          elif rule['enabled'] == True and rule_name == rule['name']:
            return(rule['name'] + ": Rule is already enabled")
        page_number = page_number + 1
        rules = self.get_rules(page_size,page_number)
        allrules = rules['data']
    return rule['name'] + ": Rule not found"

  # Elastic Integration functions

  def get_integrations(self):
      endpoint  = 'fleet/epm/packages'
      integration_objects = self.send_api_request(endpoint, 'GET')
      return integration_objects
  
  def install_integration(self, integration_name, version):
      body = {
          "force": True
      }
      body_JSON = dumps(body)
      endpoint  = 'fleet/epm/packages/' + integration_name + "-" + version
      if not self.module.check_mode:
        integration_install = self.send_api_request(endpoint, 'POST', data=body_JSON)
      else:
        integration_install = "Cannot proceed with check_mode set to " + self.module.check_mode
      return integration_install
  
  def check_integration(self, integration_name):
      integration_objects = self.get_integrations()
      integration_object = None
      for integration in integration_objects['response']:
        if integration['title'] in integration_name:
          integration_object = integration
          if integration['status'] != 'installed':
            integration_install = self.install_integration(integration['name'],integration['version'])
      return integration_object

  # Elastic Integration Package Policy functions

  def get_all_pkg_policies(self):
      endpoint  = 'fleet/package_policies'
      pkgpolicy_objects = self.send_api_request(endpoint, 'GET')
      return pkgpolicy_objects
  
  def update_pkg_policy(self,pkgpolicy_id,body):
      endpoint = "fleet/package_policies/" + pkgpolicy_id
      if not self.module.check_mode:
        pkg_policy_update = self.send_api_request(endpoint, 'PUT', data=body)
      else:
        pkg_policy_update = "Cannot proceed with check_mode set to " + self.module.check_mode
      return pkg_policy_update
  
  def get_pkg_policy(self,integration_name, agent_policy_id):
    pkg_policy_objects = self.get_all_pkg_policies()
    pkg_policy_object = None
    for pkgPolicy in pkg_policy_objects['items']:
      if pkgPolicy['package']['title'] == integration_name and pkgPolicy['policy_id'] == agent_policy_id:
        pkg_policy_object = pkgPolicy
        continue
    return pkg_policy_object
  
  def create_pkg_policy(self,pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace="default"):
    pkg_policy_object = self.get_pkg_policy(integration_object['name'],agent_policy_id)
    if not pkg_policy_object:
      body = {
        "name": pkg_policy_name,
        "namespace": namespace.lower(),
        "description": pkg_policy_desc,
        "enabled": True,
        "policy_id": agent_policy_id,
        "output_id": "",
        "inputs": [],
        'package': {
          'name': integration_object['name'],
          'title': integration_object['title'],
          'version': integration_object['version']
        }
      }
      body_JSON = dumps(body)
      endpoint = 'fleet/package_policies'
      if not self.module.check_mode:
        pkg_policy_object = self.send_api_request(endpoint, 'POST', data=body_JSON)
      else:
        pkg_policy_object = "Cannot proceed with check_mode set to " + self.module.check_mode
    return pkg_policy_object

    
# Elastic Agent Policy functions

  def get_all_agent_policys(self):
    endpoint  = 'fleet/agent_policies'
    agent_policy_objects = self.send_api_request(endpoint, 'GET')
    return agent_policy_objects

  def create_agent_policy(self, agent_policy_id, agent_policy_name, agent_policy_desc, namespace="default"):
    if agent_policy_id:
      agent_policy_object = self.get_agent_policy_byid(agent_policy_id)
    else:
      agent_policy_object = self.get_agent_policy_byname(agent_policy_name)
      
    if not agent_policy_object:
      body = {
          "name": agent_policy_name,
          "namespace": namespace.lower(),
          "description": agent_policy_desc,
          "monitoring_enabled": []
      }
      body_JSON = dumps(body)
      
      if not self.module.check_mode:
        endpoint  = 'fleet/agent_policies'
        agent_policy_object = self.send_api_request(endpoint, 'POST', data=body_JSON)
        agent_policy_object = agent_policy_object['item']
      else:
        agent_policy_object = "Cannot proceed with check_mode set to " + self.module.check_mode
    return agent_policy_object

  def get_agent_policy_byname(self, agent_policy_name):
    agent_policy_object = None
    agent_policy_objects = self.get_all_agent_policys()
    for agent_policy in agent_policy_objects['items']:
        if agent_policy['name'] == agent_policy_name:
            agent_policy_object = agent_policy
            continue
    return agent_policy_object
 
  
  def get_agent_policy_byid(self, agent_policy_id):
    endpoint  = 'fleet/agent_policies/' + agent_policy_id
    agent_policy_object = self.send_api_request(endpoint, 'GET')
    return agent_policy_object['item']

# Elastic Agent functions

  def get_agent_list(self):
    page_size = 50
    page_number = 1
    endpoint  = "fleet/agents?page=" + str(page_number) + "&perPage=" + str(page_size)
    agent_list = self.send_api_request(endpoint, 'GET')
    noOfAgents = agent_list['total']
    #agent_list_result = agent_list['list']
    agent_list_result = agent_list
    while noOfAgents > page_size * (page_number - 1):
      agent_no = 0
      endpoint  = "fleet/agents?page=" + str(page_number) + "&perPage=" + str(page_size)
      agent_list_page = self.send_api_request(endpoint, 'GET')
      while agent_no < len(agent_list_page['list']):
        agent_list_result['list'].append(agent_list_page['list'][agent_no])   
        agent_no = agent_no + 1
      page_number = page_number + 1
    return agent_list_result 