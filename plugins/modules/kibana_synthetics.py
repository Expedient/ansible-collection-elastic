#!/usr/bin/python
# Copyright 2026 Expedient
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
module: kibana_synthetics

short_description: Create a Synthetics monitor in Kibana

version_added: 2.16.0

author: Expedient

requirements:
  - python3

description:
  - "This module creates or deletes a Synthetics monitor in Kibana"
  - "supports http, tcp, icmp, and browser monitor types"
  - "if a monitor with the given name already exists, it is left untouched"
  - "if state is absent, only monitor_name and auth options are required"

options:
  state:
    description:
      - whether the monitor should exist
    choices: ['present', 'absent']
    default: present
    type: str
  monitor_name:
    description:
      - name of the monitor to create or delete
    required: True
    type: str
  monitor_type:
    description:
      - type of monitor to create
      - required when state is present
    choices: ['http', 'tcp', 'icmp', 'browser']
    type: str
  monitor_host:
    description:
      - hostname or IP address to check
      - required for icmp and tcp monitor types
      - for tcp, may optionally include a port, e.g. example.com:9200
    type: str
  url:
    description:
      - URL to check
      - required for http monitor types
    type: str
  inline_script:
    description:
      - inline Playwright/synthetics script to run
      - required for browser monitor types
    type: str
  schedule:
    description:
      - how often, in minutes, to run the monitor
    choices: [1, 3, 5, 10, 15, 30, 60, 120, 240]
    default: 5
    type: int
  locations:
    description:
      - list of Elastic-hosted location ids to run the monitor from
      - at least one of locations or private_locations is required
    type: list
    elements: str
  private_locations:
    description:
      - list of private location names to run the monitor from
      - at least one of locations or private_locations is required
    type: list
    elements: str

extends_documentation_fragment:
  - expedient.elastic.elastic_auth_options.documentation
'''

EXAMPLES = r'''
- name: create an icmp synthetic monitor
  expedient.elastic.kibana_synthetics:
    host: expedient-networks.kb.elastic.expedient.cloud
    port: 9243
    api_key: "{{ kibana_api_key }}"
    monitor_name: echo-health-vpan02.custcbb.local
    monitor_type: icmp
    monitor_host: echo-health-vpan02.custcbb.local
    private_locations:
      - cle2-ism
    schedule: 5

- name: delete a synthetic monitor
  expedient.elastic.kibana_synthetics:
    host: expedient-networks.kb.elastic.expedient.cloud
    port: 9243
    api_key: "{{ kibana_api_key }}"
    monitor_name: echo-health-vpan02.custcbb.local
    state: absent
'''

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

from ansible.module_utils.basic import AnsibleModule
from urllib.error import HTTPError


def build_monitor_body(params):
  monitor_type = params.get('monitor_type')
  body = {
    'type': monitor_type,
    'name': params.get('monitor_name'),
    'schedule': params.get('schedule'),
  }

  if params.get('locations') is not None:
    body['locations'] = params.get('locations')
  if params.get('private_locations') is not None:
    body['private_locations'] = params.get('private_locations')

  if monitor_type in ('icmp', 'tcp'):
    body['host'] = params.get('monitor_host')
  elif monitor_type == 'http':
    body['url'] = params.get('url')
  elif monitor_type == 'browser':
    body['inline_script'] = params.get('inline_script')

  return body


def validate_present_params(module):
  monitor_type = module.params.get('monitor_type')
  if not monitor_type:
    module.fail_json(msg='monitor_type is required when state is present')

  type_field = {
    'icmp': 'monitor_host',
    'tcp': 'monitor_host',
    'http': 'url',
    'browser': 'inline_script',
  }[monitor_type]
  if not module.params.get(type_field):
    module.fail_json(msg=f'{type_field} is required when monitor_type is {monitor_type}')

  if not module.params.get('locations') and not module.params.get('private_locations'):
    module.fail_json(msg='one of locations or private_locations is required when state is present')


def main():
  module_args = dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=9243),
    username=dict(type='str'),
    password=dict(type='str', no_log=True),
    api_key=dict(type='str', no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
    monitor_name=dict(type='str', required=True),
    monitor_type=dict(type='str', choices=['http', 'tcp', 'icmp', 'browser']),
    monitor_host=dict(type='str'),
    url=dict(type='str'),
    inline_script=dict(type='str'),
    schedule=dict(type='int', default=5, choices=[1, 3, 5, 10, 15, 30, 60, 120, 240]),
    locations=dict(type='list', elements='str'),
    private_locations=dict(type='list', elements='str'),
    deployment_info=dict(type='dict', default=None)
  )

  module = AnsibleModule(
    argument_spec=module_args,
    required_one_of=[('username', 'api_key')],
    required_together=[('username', 'password')],
    mutually_exclusive=[('username', 'api_key'), ('password', 'api_key')],
    supports_check_mode=True
  )

  state = module.params.get('state')
  monitor_name = module.params.get('monitor_name')
  results = {'changed': False}

  if state == 'present':
    validate_present_params(module)

  try:
    kibana = Kibana(module)
    monitor = kibana.get_synthetics_monitor_by_name(monitor_name)
  except HTTPError as e:
    module.fail_json(msg=f'Error looking up monitor {monitor_name}: {e.read()}')

  if state == 'absent':
    if not monitor:
      results['msg'] = f'monitor named {monitor_name} is already absent'
      module.exit_json(**results)

    results['changed'] = True
    results['msg'] = f'monitor named {monitor_name} will be deleted'
    results['monitor'] = monitor
    if not module.check_mode:
      try:
        kibana.delete_synthetics_monitor(monitor['id'])
      except HTTPError as e:
        module.fail_json(msg=f'Error deleting monitor {monitor_name}: {e.read()}')
      results['msg'] = f'monitor named {monitor_name} deleted'
    module.exit_json(**results)

  if monitor:
    results['msg'] = f'monitor named {monitor_name} already exists'
    results['monitor'] = monitor
    module.exit_json(**results)

  results['changed'] = True
  results['msg'] = f'monitor named {monitor_name} will be created'
  if not module.check_mode:
    body = build_monitor_body(module.params)
    try:
      results['monitor'] = kibana.create_synthetics_monitor(body)
    except HTTPError as e:
      module.fail_json(msg=f'Error creating monitor {monitor_name}: {e.read()}')
    results['msg'] = f'monitor named {monitor_name} created'
  module.exit_json(**results)


if __name__ == '__main__':
  main()
