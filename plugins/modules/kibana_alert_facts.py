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

#from plugins.modules.ece_cluster import DOCUMENTATION


ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: kibana_alert_facts

short_description: get info on a kibana alert

version_added: 2.11.1

author: Mike Garuccio (@mgaruccio)

requirements:
  - python3

description:
  - "This module gets facts about kibana alerts"
  
options:
  alert_name:
    description:
      - name of the alert to create
    required: True
    type: str
    
extends_documentation_fragment:
  - expedient.elastic.elastic_auth_options.documentation
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


def main():
  module_args=dict(
    host=dict(type='str'),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
    alert_name=dict(type='str', required=True),
    deployment_info=dict(type='dict', default=None)
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

  kibana = Kibana(module)
  results['alert_config'] = kibana.get_alert_by_name(module.params.get('alert_name'))
  module.exit_json(**results)


if __name__ == '__main__':
  main()