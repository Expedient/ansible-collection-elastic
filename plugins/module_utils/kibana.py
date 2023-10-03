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

from operator import contains
from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
from urllib.error import HTTPError
import urllib.parse
import requests
import tempfile
import os

try:
  import ansible_collections.expedient.elastic.plugins.module_utils.lookups as lookups
except:
  import sys
  import os
  util_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  import lookups as lookups

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece_apiproxy import ECE_API_Proxy
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece_apiproxy import ECE_API_Proxy

class Kibana(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.version = None # this is a hack to make it so that we can run the first request to get the clutser version without erroring out
    self.deployment_info = module.params.get('deployment_info')
    if self.deployment_info:
      self.ece_api_proxy = ECE_API_Proxy(module)
    else:
      self.version = self.get_cluster_version()
      self.major_version,self.minor_version,self.patch_version = self.version.split(".")

  def send_api_request(self, endpoint, method, data = None, headers = {}, timeout = 600, space_id = "default", no_kbnver = False,*args, **kwargs):
    
    if self.deployment_info:
      result = self.ece_api_proxy.send_api_request(endpoint, method, data, headers, timeout, space_id, no_kbnver)
    else:
      result = self.send_kibana_api_request(endpoint, method, data, headers, timeout, space_id, no_kbnver)
    return result

  def send_kibana_api_request(self, endpoint, method, data=None, headers={}, timeout = 600, space_id = "default", no_kbnver = False, *args, **kwargs):
    
    if space_id != "default":
      url = f'https://{self.host}:{self.port}/s/{space_id}/api/{endpoint}'
    else:
      url = f'https://{self.host}:{self.port}/api/{endpoint}'

    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    if self.version and no_kbnver == False:
      headers['kbn-version'] = self.version
    try:
      response = open_url(
        url, 
        data=payload, 
        method=method, 
        validate_certs=self.validate_certs, 
        headers=headers,
        force_basic_auth=True, 
        url_username=self.username, 
        url_password=self.password, 
        timeout=timeout)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    if response.msg == 'No Content' and str(response.status).startswith('2'):
      return
    else:
      response_output = response.read()
      response_str = response_output.decode()
      response_return = str(response_str).split('\n')
      response_list = []
      for i in response_return:
        return_load = loads(i)
        response_list.append(return_load)
      if len(response_list) > 1:
        return response_list
      else:
        return response_list[0]
  
  def send_epr_api_request(self, endpoint, method, data=None, headers={}, timeout=600):
    url = f'https://epr.elastic.co/{endpoint}'
    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    if self.version:
      headers['kbn-version'] = self.version
    try:
      response = open_url(url, data=payload, method=method, validate_certs=self.validate_certs, headers=headers,
                          force_basic_auth=True, url_username=self.username, url_password=self.password, timeout=timeout)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.read())

  def send_file_api_request(self, endpoint, method, data = None,  headers = {}, file = None, timeout = 600, space_id = "default", no_kbnver = False,*args, **kwargs):
    
    if self.deployment_info:
      result = self.ece_api_proxy.send_file_api_request(endpoint, method, data, headers, file, timeout, space_id, no_kbnver)
    else:
      result = self.send_kibana_file_api_request(endpoint, method, data, headers, file, space_id, timeout )
    return result

  def send_kibana_file_api_request(self, endpoint, method, data=None, headers={}, file=None, space_id = "default", timeout = 600, *args, **kwargs):

    if space_id != "default":
      url = f'https://{self.host}:{self.port}/s/{space_id}/api/{endpoint}'
    else:
      url = f'https://{self.host}:{self.port}/api/{endpoint}'
      
    headers = {}

    response = None
    
    if data:
      headers['Content-Type'] = 'application/json'
      
    if self.version:
      headers['kbn-version'] = self.version
    
    if method == "POST":
      try:
        response = requests.post(
          url, 
          auth=(self.username, self.password),
          files={'file': open(file,'rb')}, 
          headers=headers,
          timeout=timeout
        )
      except HTTPError as e:
        raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.content.decode())

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
    rule_params = self.module.params.get('rule_params')

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
    
    else:
      formatted_params = rule_params

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
  
  def format_action_config(self, action_type, config):
    if action_type == 'Webhook':
      return {
        'method': config['method'],
        'hasAuth': config['auth'],
        'url': config['url'],
        'headers': config['headers']
      }
    if action_type == 'Email':
      return {
        'from': config['sender'],
        'hasAuth': config['auth'],
        'host': config['host'],
        'port': config['port']
      }

  def format_action_secrets(self, action_type, secrets):
    secrets = {}
    if action_type == 'webhook' and 'user' in secrets:
      secrets['user'] = secrets['user']
      secrets['password'] = secrets['password']
    return secrets
    
  def create_action(self, action_type_id, action_name, config, secrets):
    endpoint = 'actions/connector'
    data = {
      'connector_type_id': action_type_id,
      'name': action_name,
      'config': config,
      'secrets': secrets
    }
    action_object = self.send_api_request(endpoint, 'POST', data=data)
    return action_object

  def delete_action(self, action):
    endpoint = f'actions/connector/{action["id"]}'
    action_object = self.send_api_request(endpoint, 'DELETE')
    return action_object
   
  # Elastic Security Rules functions

  def get_security_rule_byid(self, rule_id):
    endpoint = "detection_engine/rules?id=" + str(rule_id)
    rule_object = self.send_api_request(endpoint, 'GET')
    return rule_object

  def update_security_rule(self, body):
    endpoint = "detection_engine/rules"
    rule_object = self.get_security_rule_byid(body['id'])
    rule_object.pop('updated_at')
    rule_object.pop('updated_by')
    rule_object.pop('created_at')
    rule_object.pop('created_by')
    rule_object.pop('execution_summary')
    rule_object.pop('rule_id')
    rule_object.pop('related_integrations')
    rule_object.pop('immutable')
    rule_object.pop('required_fields')
    rule_object.pop('setup')
    rule_object.pop('revision')
    rule_object.update(body)
    update_rule = self.send_api_request(endpoint, 'PUT', data=rule_object)
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

  def get_security_rule_byname(self, rule_name, filter = "alert.attributes.name"):
    page_no = 1
    page_size = 100
    filter_scrubbed = urllib.parse.quote(str(rule_name))
    endpoint = f"detection_engine/rules/_find?page={str(page_no)}&per_page={str(page_size)}&filter={filter}:{filter_scrubbed}"
    target_rule = None
    rules = self.send_api_request(endpoint, 'GET')
    for rule in rules['data']:
      if rule['name'] == rule_name:
        target_rule = rule
    return target_rule
  
  def enable_security_rule(self,rule_id):
    body={
      'enabled': True,
      'id': rule_id
    }
    update_rule = self.update_security_rule(body)
    return update_rule
  
  def enable_security_rule_action(
      self, 
      rule_id, 
      action_id, 
      action_type, 
      body, 
      replace_or_append, 
      existing_actions, 
      action_group = 'default'
    ):
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

  def activate_security_rule(self, rule_name, page_size = 500):

    #### Getting first page of rules
    page_number = 1
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
    if 'self.major_version' in locals():
      major_version = self.major_version
      minor_version = self.minor_version
    else:
      [major_version,minor_version,patch_version] = self.deployment_info['version'].split('.')
      
    if int(major_version) > 8 or (int(major_version) == 8 and int(minor_version) >= 6):
      all_integration_flag = "prerelease"
    else:
      all_integration_flag = "experimental"
    endpoint  = f'fleet/epm/packages?{all_integration_flag}=true'
    integration_objects = self.send_api_request(endpoint, 'GET')
    return integration_objects
  
  def install_integration(self, integration_name, version):
      body = {
          "force": True
      }
      body_JSON = dumps(body)

      endpoint  = 'fleet/epm/packages/' + integration_name + "/" + version
      if not self.module.check_mode:
        integration_install = self.send_api_request(endpoint, 'POST', data=body_JSON)
      else:
        integration_install = "Cannot proceed with check_mode set to " + self.module.check_mode
      return integration_install
  
  def check_integration(self, integration_title = None, integration_name = None, *args, **kwargs):
      integration_objects = self.get_integrations()
      integration_detail_object = None
      for integration in integration_objects['items']:
        if integration_title:
          if integration['title'].upper() == integration_title.upper():
            if integration['status'] != 'installed':
              integration_install = self.install_integration(integration['name'],integration['version'])
            integration_detail_object = self.get_integration(integration['name'],integration['version'])
            break
        if integration_name:
          if integration['name'].upper() == integration_name.upper():
            if integration['status'] != 'installed':
              integration_install = self.install_integration(integration['name'],integration['version'])
            integration_detail_object = self.get_integration(integration['name'],integration['version'])
            break
      return integration_detail_object
  
  def get_integration(self, integration_name, version = None):
    endpoint  = 'fleet/epm/packages/' + integration_name + "/" + version       
    integration_object = self.send_api_request(endpoint, 'GET')
    integration_object = integration_object['item']
    return integration_object

  def update_integration(self, integration_name, integration_version, body, *args, **kwargs):
    
    endpoint  = f'fleet/epm/packages/{integration_name}/{integration_version}'
    body_JSON = dumps(body)
    integration_object = self.send_api_request(endpoint, 'PUT', data=body_JSON)
    integration_object = integration_object['item']
    return integration_object
        
  # Elastic Integration Package Policy functions

  def get_all_pkg_policies(self, perPage = 500):
      endpoint  = 'fleet/package_policies?perPage='+ str(perPage)
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
  
  def get_elatic_package_repository_package_info(self, package_name, package_version):
    endpoint = "package/" + package_name + "/" + package_version
    epr_object = self.send_epr_api_request(endpoint, 'GET')
    return epr_object
  
  def create_pkg_policy(self,pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, space_id="default", var_list=None):
    pkg_policy_object = self.get_pkg_policy(pkg_policy_name)
    epr_object = self.get_elatic_package_repository_package_info(integration_object['name'], integration_object['version'])

    inputs_body = []
    if var_list:
      var_list_JSON = loads(var_list)
    else:
      var_list_JSON = None
      
    if not pkg_policy_object:

      if 'policy_templates' in epr_object:
        for epr_policy_template in epr_object['policy_templates']:
          if 'inputs' in epr_policy_template:
            for epr_inputs in epr_policy_template['inputs']:
              inputs_entry = {}         
              inputs_entry['policy_template'] = epr_policy_template['name']
              if epr_inputs['title'].find("(experimental)") >= 0:
                inputs_entry['enabled'] = False
              else:
                inputs_entry['enabled'] = True
              inputs_entry['type'] = epr_inputs['type']
              if 'config' in inputs_entry:
                inputs_entry['config'] = epr_inputs['config']
              else:
                inputs_entry['config'] = {}
              if 'vars' in epr_inputs:
                inputs_entry['vars'] = {}
                for epr_inputs_var in epr_inputs['vars']:
                  epr_inputs_var.pop('title')
                  epr_inputs_var.pop('multi')
                  epr_inputs_var.pop('required')
                  epr_inputs_var.pop('show_user')
                  if 'description' in epr_inputs_var: 
                    epr_inputs_var.pop('description')
                  if 'default' in epr_inputs_var:
                    epr_inputs_var['value'] = epr_inputs_var['default']
                    epr_inputs_var.pop('default')
                  var_name = epr_inputs_var['name']
                  epr_inputs_var.pop('name')
                  inputs_entry['vars'][var_name] = epr_inputs_var
                  #inputs_entry['vars'].update(epr_inputs_var)
              else:
                inputs_entry['vars'] = {}
              if 'config' in epr_inputs:
                inputs_entry['config'] = epr_inputs['config']
              inputs_entry['streams'] = []                
              for epr_data_stream in epr_object['data_streams']:
                if 'streams' in epr_data_stream:
                  for epr_stream in epr_data_stream['streams']:
                    if epr_inputs['type'] == epr_stream['input']:
                      inputs_body_streams_entry = {}
                      inputs_body_streams_entry['enabled'] = epr_stream['enabled']
                      inputs_body_streams_entry['data_stream'] = {}
                      inputs_body_streams_entry['data_stream']['dataset'] = epr_data_stream['dataset']
                      inputs_body_streams_entry['data_stream']['type'] = epr_data_stream['type']
                      if 'vars' in epr_stream:
                        inputs_body_streams_entry['vars'] = {}
                        for epr_stream_var in epr_stream['vars']:
                          inputs_body_streams_var_entry = {}
                          epr_stream_var.pop('title')
                          epr_stream_var.pop('multi')
                          epr_stream_var.pop('required')
                          epr_stream_var.pop('show_user')
                          if 'description' in epr_stream_var:
                            epr_stream_var.pop('description')
                          var_name = epr_stream_var['name']
                          epr_stream_var.pop('name')
                          if 'default' in epr_stream_var:
                            epr_stream_var['value'] = epr_stream_var['default']
                            epr_stream_var.pop('default')
                          if var_list_JSON != None:
                            for var_JSON in var_list_JSON:
                              for var_key, var_value in var_JSON.items():
                                var_key_type, var_key_name = var_key.split(':')
                                if var_key_type == epr_inputs['type'] and var_name == var_key_name:
                                  epr_stream_var['value'] = var_value
                          inputs_body_streams_var_entry[var_name] = epr_stream_var
                          inputs_body_streams_entry['vars'].update(inputs_body_streams_var_entry)
                      if inputs_body_streams_entry:
                        inputs_entry['streams'].append(inputs_body_streams_entry)
              inputs_body.append(inputs_entry)

      body = {
        "name": pkg_policy_name,
        "namespace": space_id.lower(),
        "description": pkg_policy_desc,
        "force": True,
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

  def get_agentpolicy_enrollment_tokens(self, perPage = 500):
    endpoint  = 'fleet/enrollment_api_keys?perPage='+ str(perPage)
    enrollment_api_objects = self.send_api_request(endpoint, 'GET')
    return enrollment_api_objects

  def get_all_agent_policys(self, perPage = 500):
    endpoint  = 'fleet/agent_policies?perPage='+ str(perPage)
    agent_policy_objects = self.send_api_request(endpoint, 'GET')
    return agent_policy_objects

  def create_agent_policy(self, agent_policy_id, agent_policy_name, agent_policy_desc, space_id="default", monitoring=[]):
    if agent_policy_id:
      agent_policy_object = self.get_agent_policy_byid(agent_policy_id)
    else:
      agent_policy_object = self.get_agent_policy_byname(agent_policy_name)
      
    if not agent_policy_object:
      body = {
          "name": agent_policy_name,
          "namespace": space_id.lower(),
          "description": agent_policy_desc,
          "monitoring_enabled": monitoring
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

  def get_agent_list(self, page_size = 500, page_number = 1) :
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

# Elastic Saved Objects

  def get_saved_object(
    self, 
    object_type, 
    object_name = None, 
    object_id = None, 
    space_id = 'default', 
    *args, 
    **kwargs
    ):
    page_size = 500
    page_number = 1
    target_object = ""
    if object_id == None:
      object_name_quote = urllib.parse.quote(object_name)
      endpoint  = f'saved_objects/_find?type={object_type}&search_fields=name&search_fields=title&search={object_name_quote}&page={str(page_number)}&per_page={str(page_size)}'
      found_objects = self.send_api_request(endpoint, 'GET', space_id = space_id)
      for found_object in found_objects['saved_objects']:
        if 'name' in found_object['attributes']:
          if object_name == found_object['attributes']['name']:
            target_object = found_object
            break
        if 'title' in found_object['attributes']:
          if object_name == found_object['attributes']['title']:
            target_object = found_object
            break
    else:
      endpoint  = f'saved_objects/{object_type}/{object_id}'
      target_object = self.send_api_request(endpoint, 'GET', space_id = space_id)
    return target_object

  def get_saved_objects_list(self, object_string, object_type, space_id = 'default'):
    page_size = 500
    page_number = 1
    object_name_quote = urllib.parse.quote(object_string)
    endpoint  = f'saved_objects/_find?type={object_type}&search_fields=name&search_fields=title&search={object_name_quote}&page={str(page_number)}&per_page={str(page_size)}'
    found_objects = self.send_api_request(endpoint, 'GET', space_id = space_id)
    return found_objects

  def update_saved_object(self, saved_object, object_type, object_id, object_attributes, *args, **kwargs):
    endpoint  = f'saved_objects/{object_type}/{object_id}'
    body_JSON = dumps(saved_object)
    updated_object = self.send_api_request(endpoint, 'PUT', data = body_JSON)
    return updated_object
  
  def export_saved_object(self,
      object_type, 
      object_id, 
      space_id = "default", 
      includeReferencesDeep = True, 
      excludeExportDetails = True, 
      *args, 
      **kwargs 
    ):
    endpoint = "saved_objects/_export"
    object = {
      "type": object_type,
      "id": object_id
    }
    body = {
      "includeReferencesDeep": includeReferencesDeep,
      "excludeExportDetails": excludeExportDetails
    }
    objects = []
    objects.append(object)
    body['objects'] = objects
    #body['excludeExportDetails'] = True
    body_JSON = dumps(body)
    headers = {}
    headers['kbn-xsrf'] = True
    export_object = self.send_api_request(endpoint, 'POST', data=body_JSON, headers = headers, space_id = space_id, no_kbnver = True)
    return export_object

  def import_saved_object(self, object_attributes, space_id = "default", overwrite = False, createNewCopies = True):
    importObjectJSON = tempfile.NamedTemporaryFile(delete=False,suffix='.ndjson', prefix='saved_object_')
    #object_attributes_json = loads(object_attributes)
    import_file = open(importObjectJSON.name, 'a')
    #for i in object_attributes_json:
    #  import_file.write(dumps(i) + '\n')
    import_file.write(object_attributes)
    import_file.close()
    importObjectJSON.close()
    endpoint = f'saved_objects/_import?createNewCopies={createNewCopies}&overwrite={overwrite}'
    import_object = self.send_file_api_request(endpoint, 'POST', file=importObjectJSON.name, space_id = space_id)
    os.remove(importObjectJSON.name)
    return import_object

  def get_fleet_server_hosts(self):
    endpoint = 'fleet/settings'
    result = self.send_api_request(endpoint, 'GET')
    return result['item']['fleet_server_hosts']

  def set_fleet_server_hosts(self, hosts: list, name='Default', default=True):
    endpoint = 'fleet/fleet_server_hosts/fleet-default-fleet-server-host' 
    headers = {'kbn-xsrf': True}
    body = {
        'is_default': default,
        'name': name,
        'host_urls': hosts
      }

    result = self.send_api_request(endpoint, 'PUT', headers=headers, data=body)
    return result

  def get_fleet_elasticsearch_hosts(self):
    endpoint = 'fleet/outputs'
    result = self.send_api_request(endpoint, 'GET')
    for item in result['items']:
      if item['id'] == "fleet-default-output" and item['type'] == 'elasticsearch':
        return item['hosts']

  def set_fleet_elasticsearch_hosts(self, hosts: list):
    endpoint = 'fleet/outputs/fleet-default-output'
    body = {
      'hosts': hosts
    }

    body_json = dumps(body)

    result = self.send_api_request(endpoint, 'PUT', data=body_json)
    return result

# Elastic Space

  def get_space(self, id, *args, **kwargs ):
      endpoint  = f'spaces/space'
      spaces = self.send_api_request(endpoint, 'GET')
      target_space = None
      for space in spaces:
        if space['id'] == id:
          target_space = space
          break
      return target_space

  def create_space(
    self, 
    id, 
    name, 
    description = None, 
    disabledFeatures = None, 
    initials = None, 
    color = None,
    imageUrl = None,
    *args, 
    **kwargs
    ):
    endpoint  = f'spaces/space'
    body = {
      "id": id,
      "name": name
    }
    if description != None:
      body['description'] = description
    if disabledFeatures != None:
      body['disabledFeatures'] = disabledFeatures
    else:
      body['disabledFeatures'] = []
    if initials != None:
      body['initials'] = initials
    if color != None:
      body['color'] = color
    if imageUrl != None:
      body['imageUrl'] = imageUrl
    body_json = dumps(body)
    result = self.send_api_request(endpoint, 'POST', data = body_json)
    return result

  def update_space(
    self, 
    id, 
    name, 
    description = None, 
    disabledFeatures = None, 
    initials = None, 
    color = None,
    imageUrl = None,
    *args, 
    **kwargs
    ):
    endpoint  = f'spaces/space/' + id
    body = {
      "id": id,
      "name": name
    }
    if description != None:
      body['description'] = description
    if disabledFeatures != None:
      body['disabledFeatures'] = disabledFeatures
    else:
      body['disabledFeatures'] = []
    if initials != None:
      body['initials'] = initials
    if color != None:
      body['color'] = color
    if imageUrl != None:
      body['imageUrl'] = imageUrl
    body_json = dumps(body)
    result = self.send_api_request(endpoint, 'PUT', data = body_json)
    return result
 
# Elastic User Role
  
  def get_userrole(self, name):
    endpoint  = f'security/role/{name}'
    userrole_object = self.send_api_request(endpoint, 'GET')
    return userrole_object

  def create_userrole(self, 
                   name, 
                   body = None, 
                   *args, 
                   **kwargs ):
    if body == None or body == "":
      body = { 
        "metadata": { 
          "version" : 1 
        }, 
        "elasticsearch": { 
          "cluster" : [],
          "indices" : []
        },
        "kibana": []
      }
    endpoint  = f'security/role/{name}'
    body_json = dumps(body)
    result = self.send_api_request(endpoint, 'PUT', data = body_json)
    return result

# Kibana Settings

  def get_kibana_settings(self, space_id = 'default', *args, **kwargs ):
    endpoint  = f'kibana/settings'
    kibana_settings = self.send_api_request(endpoint, 'GET', space_id = space_id)
    return kibana_settings

  def update_kibana_settings(self, settings, space_id = 'default', *args, **kwargs ):
    for setting, value in settings.items():
      endpoint  = f'kibana/settings/{setting}'
      body = {
        "value": value
      } 
      body_json = dumps(body)
      result = self.send_api_request(endpoint, 'POST', data = body_json, space_id = space_id)
    return result
  
# Exception Lists

  def get_security_exception_list(self, namespace_type = 'agnostic', space_id = 'default'):
    endpoint = f'exception_lists/_find?namespace_type={namespace_type}'
    result = self.send_api_request(endpoint, 'GET', space_id = space_id)
    return result['data']

  def get_security_exception_list_item(self, list_id = 'endpoint_list', namespace_type = 'agnostic', space_id = 'default'):
    endpoint = f'exception_lists/items/_find?list_id={list_id}&namespace_type={namespace_type}'
    result = self.send_api_request(endpoint, 'GET', space_id = space_id)
    return result['data']
  
  def create_security_exception_list_items(self, id, body, space_id = 'default', namespace_type = 'agnostic'):
    endpoint = f'exception_lists/items?id={id}&namespace_type={namespace_type}'
    #json_body = dumps(body)
    result = self.send_api_request(endpoint, 'POST', data = body, space_id = space_id)
    return result
  
  def delete_security_exception_list_items(self, item_id, space_id = 'default', namespace_type = 'agnostic'):
    endpoint = f'exception_lists/items?item_id={item_id}&namespace_type={namespace_type}'
    result = self.send_api_request(endpoint, 'DELETE', space_id = space_id)
    return result
  
# Data View

  def set_dataview_default(self, dataview_id = "logs-*"):
    endpoint = f'data_views/default'
    body = {
      "data_view_id": dataview_id,
      "force": True
    }
    body_json = dumps(body)
    result = self.send_api_request(endpoint, 'POST', data = body_json)
    return result