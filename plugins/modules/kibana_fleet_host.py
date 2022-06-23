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
module: kibana_fleet_host

short_description: Add host to kibana fleet

version_added: 2.3.0 # change this

author: Mac Masterson (@maclin-masterson)

requirements:
  - python3

description:
  - "This module adds a host endpoint to a kibana fleet"

options:
    host:
        description:
            - The Kibana Host you're updating
        type: str
    username:
        description:
            - Elastic Username
        type: str
    password:
        description:
            - Elastic Password
        type: str
    verify_ssl_cert:
        description:
            - Whether or not to verify SSL cert on API requests
        type: bool
    urls:
        description:
            - List of urls that you want to apply as a fleet server host or an elasticsearch host
        type: list
        element type: str
    url_type:
        description:
            - The url type that you want to set for the fleet
            - 'server' sets the fleet server host
            - 'elasticsearch' sets the fleet elasticsearch host
        options:
            - fleet_server
            - elasticsearch
    action:
        description:
            - The action that you want the module to take against the fleet server
            - Add: Add the provided urls to the fleet
            - Remove: Remove the provided urls from the fleet
            - Overwrite: Replace the urls in the fleet with the provided urls
        options:
            - Add
            - Remove
            - Overwrite

extends_documentation_fragment:
  - expedient.elastic.elastic_auth_options.documentation
'''


try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
  import ansible_collections.expedient.elastic.plugins.module_utils.lookups
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

from ansible.module_utils.basic import AnsibleModule
from json import dumps

class KibanaFleet(Kibana):
    def __init__(self, module):
        super().__init__(module)
        self.url_type = self.module.params.get('url_type')

    def get_current_urls(self):
        if self.url_type == 'fleet_server':
            current_urls = self.get_fleet_server_hosts()
        if self.url_type == 'elasticsearch':
            current_urls = self.get_fleet_elasticsearch_hosts()
        return current_urls

    def send_urls(self, urls: list):
        if self.url_type == 'fleet_server':
            result = self.set_fleet_server_hosts(urls)

        if self.url_type == 'elasticsearch':
            result = self.set_fleet_elasticsearch_hosts(urls)

        return result


def main():
    module_args=dict(
        host=dict(type='str', required=True),
        port=dict(type='int', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        verify_ssl_cert=dict(type='bool', default=True),
        url_type=dict(type='str', choices=['fleet_server', 'elasticsearch'], required=True),
        urls=dict(type='list', elements='str', required=True),
        action=dict(type='str', choices=['add', 'overwrite', 'remove'], default='add')
    )

    results = {
        'changed': False,
        'msg': ''
        }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    kibana_fleet = KibanaFleet(module)
    action = module.params.get('action')
    current_urls = kibana_fleet.get_current_urls() # The urls as they exist in kibana at start
    provided_urls = module.params.get('urls') # Urls provided by the user

    # final_urls is a list that gets calculated depending on the provided action.
    final_urls = []

    if action == 'add':
        final_urls.extend(current_urls)
        for item in provided_urls:
            if item in current_urls:
                results['msg'] += f"\n{item} already exists in Kibana"
            else:
                final_urls.append(item)

    if action == 'overwrite':
        final_urls.extend(provided_urls)

    if action == 'remove':
        for item in current_urls:
            if item in provided_urls:
                continue

            final_urls.append(item)

    # Converting lists to sets for comparison
    if set(current_urls) == set(final_urls):
        results['msg'] += "\n No action needed"
    else:
        send_url_result = kibana_fleet.send_urls(final_urls)
        if 'message' in send_url_result:
            module.fail_json(f"Unable to {action} urls. Error: {send_url_result['message']}")
        else:
            results['changed'] = True
            results['msg'] += f"\nSuccessful {action}"
            results['fleet_server_urls'] = kibana_fleet.get_fleet_server_hosts()
            results['fleet_elasticsearch_urls'] = kibana_fleet.get_fleet_elasticsearch_hosts()

    module.exit_json(**results)


if __name__ == '__main__':
    main()
