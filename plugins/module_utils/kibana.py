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

try:
  import ansible_collections.expedient.elastic.plugins.module_utils.lookups as lookups
except:
  import sys
  import os
  util_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  import lookups as lookups

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

  def send_api_request(self, endpoint, method, data=None, headers={}):
    url = f'https://{self.host}:{self.port}/api/{endpoint}'
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
  
  def ensure_alert(self, alert_id=None):
    """
    This method will either make a POST request to create an alert,
    or a PUT request to update an alert. This distinction is made based on
    the existence of alert_id.

    variables:
      alert_id(str): Default to None. The ID of the alert that we want to update.
                     If this variable exists, then the method will do a PUT request.
                     Otherwise, it will do a POST and create a new alert.

    Returns:
      result(dict)
    """
    endpoint = 'alerting/rule'
    if alert_id:
      # Updating an alert
      endpoint += f"/{alert_id}"
      method = "PUT"
    else:
      # Creating an alert
      method="POST"

    # set variables for data
    notify_when = self.module.params.get('notify_on')
    alert_type = self.module.params.get('alert_type')
    group_by = self.module.params.get('group_by')

    data = {
      'notify_when': lookups.notify_lookup[notify_when],
      'params': self.format_alert_params(),
      'schedule': {
        'interval': self.module.params.get('check_every')
      },
      'actions': self.format_alert_actions(),
      'tags': self.module.params.get('tags'),
      'name': self.module.params.get('alert_name')
    }
    if self.module.params.get('filter'):
      data['params']['filterQueryText'] = self.module.params.get('filter')
      data['params']['filterQuery'] = self.module.params.get('filter_query')
    if group_by:
        data['params']['groupBy'] = self.module.params.get('group_by')
    if alert_id is None:
      # If we are creating a new alert
      data['rule_type_id'] = lookups.alert_type_lookup[alert_type]
      data['consumer'] = self.module.params.get('consumer')
      data['enabled']= self.module.params.get('enabled')
    result = self.send_api_request(endpoint, method, data=data)
    return result
  
  def delete_alert(self, alert_id):
    endpoint = f'alerting/rule/{alert_id}'
    return self.send_api_request(endpoint, 'DELETE')

  def format_alert_actions(self):
    actions = self.module.params.get('actions')
    formatted_actions = [{
      'group': lookups.action_group_lookup[action['run_when']],
      'params': {
        lookups.action_param_type_lookup[action['action_type']]: [action['body']] if action['body'] else dumps(action['body_json'], indent=2)
      },
      'id': self.get_alert_connector_by_name(action['connector'])['id']
    } for action in actions]
    return formatted_actions
  
  def format_alert_conditions(self):
    conditions = self.module.params.get('conditions')
    alert_type = self.module.params.get('alert_type')
    formatted_conditions = []
    if alert_type == 'metrics_threshold':
      for condition in conditions:
        formatted_condition = {
          'aggType': condition['when'],
          'comparator': lookups.state_lookup[condition['state']],
          'threshold': [condition['threshold']] if condition['threshold'] != 0.0 else [int(condition['threshold'])],
          'timeSize': condition['time_period'],
          'timeUnit': lookups.time_unit_lookup[condition['time_unit']],
        }
        if condition['field'] is not None:
          formatted_condition['metric'] = condition['field']
        formatted_conditions.append(formatted_condition)
    return formatted_conditions
  
  def format_alert_availability(self):
    availability = self.module.params.get('availability')
    formatted_availability = {}
    alert_type = self.module.params.get('alert_type')
    if alert_type == 'uptime_monitor_status':
      formatted_availability = {
        'range': availability['range'],
        'rangeUnit': lookups.time_unit_lookup[availability['rangeUnit']],
        'threshold': availability['threshold']
      }

    return formatted_availability
  
  def format_alert_params(self):
    formatted_params = {}
    alert_type = self.module.params.get('alert_type')

    if alert_type == 'metrics_threshold':
      criteria = self.format_alert_conditions()
      formatted_params = {
        'criteria': criteria,
        'alertOnNoData': self.module.params.get('alert_on_no_data'),
        'sourceId': 'default' #entirely unclear what this does but it appears to be a static value so hard-coding for now
      }
    
    elif alert_type == 'uptime_monitor_status':
      availability = self.format_alert_availability()
      formatted_params = {
        'availability': availability,
        'numTimes': self.module.params.get('numTimes'),
        'search': self.module.params.get('search'),
        'shouldCheckAvailability': self.module.params.get('shouldCheckAvailability'),
        'shouldCheckStatus': self.module.params.get('shouldCheckStatus'),
        'timerangeCount': self.module.params.get('timerangeCount'),
        'timerangeUnit': lookups.time_unit_lookup[self.module.params.get('timerangeUnit')]
      }

    if self.module.params.get('filter'):
      formatted_params['filterQueryText'] = self.module.params.get('filter')
      formatted_params['filterQuery'] = self.module.params.get('filter_query')
    if self.module.params.get('group_by'):
      formatted_params['groupBy'] = self.module.params.get('group_by')
      formatted_params['alertOnGroupDisappear'] = (
        self.module.params.get('alert_on_group_disappear')
        if self.module.params.get('alert_on_group_disappear') is not None
        else False)

    return formatted_params
  
  # Elastic Security Rules functions

  def update_security_rule(self, body):
    endpoint = "detection_engine/rules"
    update_rule = self.send_api_request(endpoint, 'PATCH', data=body)
    return update_rule

  def get_security_rules(self, page_size, page_no):
    endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size)
    rules = self.send_api_request(endpoint, 'GET')
    return rules

  def get_security_rules_byfilter(self, rule_name):
    page_no = 1
    page_size = 100
    filter_scrubbed = urllib.parse.quote(str(rule_name))
    endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size) + "&filter=alert.attributes.name:" + filter_scrubbed
    rules = self.send_api_request(endpoint, 'GET')
    return rules
  
  def enable_security_rule(self,rule_id):
    body={
      'enabled': True,
      'id': rule_id
    }
    update_rule = self.update_security_rule(body)
    return update_rule
  
  def enable_security_rule_action(self, rule_id, action_id, action_type, body, replace_or_append, existing_actions, action_group = 'default'):
    params = {
      'body': str(body)
    }
    action_def = {
      'action_type_id': action_type,
      'id': action_id,
      'group': action_group,
      'params': params
    }
    if replace_or_append == 'replace':
      body = {
        'id': rule_id,
        'throttle': "rule",
        'actions': [ action_def ]
      }  
    elif replace_or_append == 'append':
      action_def.append(existing_actions)
      body = {
        'id': rule_id,
        'actions': [ action_def ]
      } 

    #body_JSON = dumps(body)
    update_rule = self.update_security_rule(body)
    return update_rule

  def activate_security_rule(self, rule_name):

    #### Getting first page of rules
    page_number = 1
    page_size = 100
    rules = self.get_security_rules_byfilter(rule_name)
    noOfRules = rules['total']
    allrules = rules['data']
    #### Going through each rule page by page and enabling each rule that isn't enabled.
    while noOfRules > page_size * (page_number - 1):
        for rule in allrules:
          if rule['enabled'] == False and rule_name == rule['name']:
            enable_rule = self.enable_security_rule(rule['id'])
            return(rule['name'] + ": Rule is updated")
          elif rule['enabled'] == True and rule_name == rule['name']:
            return(rule['name'] + ": Rule is already enabled")
        #page_number = page_number + 1
        #rules = self.get_security_rules(page_size,page_number)
        #allrules = rules['data']
    return rule_name + ": Rule not found"

  # Elastic Integration functions

  def get_integrations(self):
      endpoint  = 'fleet/epm/packages?experimental=true'
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
  
  def check_integration(self, integration_title):
      integration_objects = self.get_integrations()
      integration_detail_object = None
      for integration in integration_objects['response']:
        if integration['title'].upper() in integration_title.upper():
          if integration['status'] != 'installed':
            integration_install = self.install_integration(integration['name'],integration['version'])
          integration_detail_object = self.get_integration(integration['name'],integration['version'])
          break
      return integration_detail_object
  
  def get_integration(self, integration_name, version):
      endpoint  = 'fleet/epm/packages/' + integration_name + "-" + version
      integration_object = self.send_api_request(endpoint, 'GET')
      integration_object = integration_object['response']
      return integration_object
    
  # Elastic Integration Package Policy functions

  def get_all_pkg_policies(self):
      perPage = "500"
      endpoint  = 'fleet/package_policies?perPage='+ perPage
      pkgpolicy_objects = self.send_api_request(endpoint, 'GET')
      return pkgpolicy_objects
  
  def update_pkg_policy(self,pkgpolicy_id,body):
      if 'id' in body:
        pkgpolicy_id = body['id']
        body.pop('id')
      if 'revision' in body:
        body.pop('revision')
      if 'created_at' in body:
        body.pop('created_at')
      if 'created_by' in body:
        body.pop('created_by')
      if 'updated_at' in body:
        body.pop('updated_at')
      if 'updated_by' in body:
        body.pop('updated_by')
      input_no = 0
      for input in body['inputs']:
        if 'streams' in input:
          streams_no = 0
          for stream in input['streams']:
            if 'id' in stream:
              body['inputs'][input_no]['streams'][streams_no].pop('id')
            if 'compiled_stream' in stream:
              body['inputs'][input_no]['streams'][streams_no].pop('compiled_stream')
            streams_no = streams_no + 1
        input_no = input_no + 1
      if not self.module.check_mode:
        endpoint = "fleet/package_policies/" + pkgpolicy_id
        pkg_policy_update = self.send_api_request(endpoint, 'PUT', data=body)
      else:
        pkg_policy_update = "Cannot proceed with check_mode set to " + self.module.check_mode
      return pkg_policy_update
  
  def get_pkg_policy(self,pkg_policy_name):
    pkg_policy_objects = self.get_all_pkg_policies()
    pkg_policy_object = ""
    for pkgPolicy in pkg_policy_objects['items']:
      if pkgPolicy['name'].upper() == pkg_policy_name.upper():
        pkg_policy_object = pkgPolicy
        break
    return pkg_policy_object
  
  def create_pkg_policy(self,pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace="default"):
    pkg_policy_object = self.get_pkg_policy(pkg_policy_name)
    inputs_body = []
    if 'policy_templates' in integration_object:
      for policy_template in integration_object['policy_templates']:
        if 'inputs' in policy_template:
          if policy_template['inputs'] != None:
            for policy_input in policy_template['inputs']:
              inputs_body_entry = {}
              inputs_body_entry['policy_template'] = policy_template['name']
              inputs_body_entry['enabled'] = True
              inputs_body_entry['type'] = policy_input['type']
              if 'config' in policy_input:                 
                inputs_body_entry['config'] = policy_input['config']
              else:
                inputs_body_entry['config'] = {}
              input_body_template_var = {}
              if 'vars' in policy_input:
                for policy_template_var in policy_input['vars']:
                  if 'value' in policy_template_var:
                    input_body_template_var[policy_template_var['name']] = { "type": policy_template_var['type'], "value": policy_template_var['value'] }
                  else:
                    input_body_template_var[policy_template_var['name']] = { "type": policy_template_var['type'] }
              inputs_body_entry['vars'] = input_body_template_var
              inputs_body_streams = []
              for integration_object_input in integration_object['data_streams']:
                inputs_body_stream_entry = {}
                #inputs_body_stream_entry['enabled'] = True
                for integration_input_stream in integration_object_input['streams']:
                  if 'enabled' in integration_input_stream:
                    inputs_body_stream_entry['enabled'] = integration_input_stream['enabled']
                  else:
                    inputs_body_stream_entry['enabled'] = False
                  if integration_input_stream['input'] == policy_input['type']:
                    inputs_body_streams_datastream = {}
                    inputs_body_streams_datastream['dataset'] = integration_object_input['dataset']
                    inputs_body_streams_datastream['type'] = integration_object_input['type']
                    inputs_body_stream_entry['data_stream'] = inputs_body_streams_datastream
                    input_body_stream_var = {}
                    for integration_stream_var in integration_input_stream['vars']:
                      if 'default' in integration_stream_var:
                        input_body_stream_var[integration_stream_var['name']] = { "type": integration_stream_var['type'], "value": integration_stream_var['default']}
                      else:
                        input_body_stream_var[integration_stream_var['name']] = { "type": integration_stream_var['type'], "value": ""}
                    inputs_body_stream_entry['vars'] = input_body_stream_var
                    inputs_body_streams.append(inputs_body_stream_entry)
                  
                inputs_body_entry['streams'] = inputs_body_streams
              inputs_body.append(inputs_body_entry)

    if not pkg_policy_object:
      body = {
        "name": pkg_policy_name,
        "namespace": namespace.lower(),
        "description": pkg_policy_desc,
        "enabled": True,
        "policy_id": agent_policy_id,
        "output_id": "",
        "inputs": inputs_body,
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

  def toggle_pkg_policy_input_onoff(self, pkg_policy_object, type, onoff):
    pkg_policy_object_updated = pkg_policy_object
    i = 0
    for input in pkg_policy_object['inputs']:
      if input['type'] == type:
        pkg_policy_object_updated['inputs'][i]['enabled'] = onoff
      i= i + 1
    return pkg_policy_object_updated
  
  def toggle_pkg_policy_stream_onoff(self, pkg_policy_object, dataset, onoff):
    pkg_policy_object_updated = pkg_policy_object
    i = 0
    for input in pkg_policy_object_updated['inputs']:
      j=0
      for streams in input['streams']:
        if 'compiled_stream' in streams:
          pkg_policy_object_updated['inputs'][i]['streams'][j].pop('compiled_stream')
        if streams['data_stream']['dataset'] == dataset:
          pkg_policy_object_updated['inputs'][i]['streams'][j]['enabled'] = onoff
        j = j + 1
      i = i + 1
    return pkg_policy_object_updated
    
# Elastic Agent Policy functions

  def get_all_agent_policys(self):
    perPage = "500"
    endpoint  = 'fleet/agent_policies?perPage='+ perPage
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
        if agent_policy['name'].upper() == agent_policy_name.upper():
            agent_policy_object = agent_policy
            continue
    return agent_policy_object
 
  def get_agent_policy_byid(self, agent_policy_id):
    endpoint  = 'fleet/agent_policies/' + agent_policy_id
    agent_policy_object = self.send_api_request(endpoint, 'GET')
    return agent_policy_object['item']
  
  def delete_agent_policy(self, agent_policy_id = None, agent_policy_name = None):
    if agent_policy_id:
      agent_policy_object = self.get_agent_policy_byid(agent_policy_id)
    else:
      agent_policy_object = self.get_agent_policy_byname(agent_policy_name)
    if agent_policy_object:
      body = {
        'agentPolicyId': str(agent_policy_object['id'])
      }
      body_JSON = dumps(body)
      endpoint = 'fleet/agent_policies/delete'
      agent_policy_object = self.send_api_request(endpoint, 'POST', body_JSON)
    else:
      agent_policy_object = ""
    return agent_policy_object

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

  def get_fleet_server_hosts(self):
    endpoint = 'fleet/settings'
    result = self.send_api_request(endpoint, 'GET')
    return result['item']['fleet_server_hosts']

  def set_fleet_server_host(self, host):
    endpoint = 'fleet/settings'
    headers = {'kbn-xsrf': True}
    body = {
        'fleet_server_hosts': [
          host
        ]
      }

    body_json = dumps(body)

    result = self.send_api_request(endpoint, 'PUT', headers=headers, data=body_json)
    return result

  def get_fleet_elasticsearch_hosts(self):
    endpoint = 'fleet/outputs'
    result = self.send_api_request(endpoint, 'GET')
    for item in result['items']:
      if item['id'] == "fleet-default-output" and item['type'] == 'elasticsearch':
        return item['hosts']

  def set_fleet_elasticsearch_host(self, host):
    endpoint = 'fleet/outputs/fleet-default-output'
    body = {
      'hosts': [
        host
      ]
    }

    body_json = dumps(body)

    result = self.send_api_request(endpoint, 'PUT', data=body_json)
    return result
