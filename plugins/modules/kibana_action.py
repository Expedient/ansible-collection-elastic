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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: kibana_action
short_description: Configure Kibana action
author:
- Mike Garuccio (@mgaruccio)
- Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Configure Kibana action.
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the module
    choices: [present, absent]
    default: present
    type: str
  action_name:
    description:
    - Action name
    type: str
  action_type:
    description:
    - Action type
    type: str
    choices: [Email, Webhook]
  config:
    description:
    - Config
    type: dict
  secrets:
    description:
    - Secrets
    type: dict
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Create Alert action
  expedient.elastic.kibana_action:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    action_name: Alert
    action_type: Webhook
    config:
    method: post
    auth: no
    url: '{{ alert_mgr_url }}/alert/{{ client_id }}'
    headers:
      Content-Type: application/json
- name: Create Heartbeat Alert action
  expedient.elastic.kibana_action:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    action_name: Heatbeat Alert
    action_type: Webhook
    config:
    method: post
    auth: no
    url: '{{ alert_mgr_url }}/elastic-alert'
    headers:
      Content-Type: application/json
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: action named Test-name will be created
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import assertRaisesRegex

try:
    from ansible_collections.expedient.elastic.plugins.module_utils.kibana import (
        Kibana,
        kibana_argument_spec,
    )
except ImportError:
    import sys
    import os

    util_path = new_path = f"{os.getcwd()}/plugins/module_utils"
    sys.path.append(util_path)
    from kibana import Kibana, kibana_argument_spec


class KibanaAction(Kibana):
    def __init__(self, module):
        super().__init__(module)
        self.module = module
        self.state = self.module.params.get("state")
        self.action_name = self.module.params.get("action_name")
        self.action_type = self.module.params.get("action_type")
        self.action_type_id = self.get_alert_connector_type_by_name(self.action_type)["id"]
        self.config = self.module.params.get("config")
        self.secrets = self.module.params.get("secrets")

        self.action = self.get_alert_connector_by_name(self.action_name)

    def format_config(self):
        if self.action_type == "Webhook":
            return {
                "method": self.config["method"],
                "hasAuth": self.config["auth"],
                "url": self.config["url"],
                "headers": self.config["headers"],
            }
        if self.action_type == "Email":
            return {"from": self.config["sender"], "hasAuth": self.config["auth"], "host": self.config["host"], "port": self.config["port"]}

    def format_secrets(self):
        secrets = {}
        if self.action_type == "webhook" and "user" in self.secrets:
            secrets["user"] = self.secrets["user"]
            secrets["password"] = self.secrets["password"]
        return secrets

    def create_action(self):
        endpoint = "actions/connector"
        data = {
            "connector_type_id": self.action_type_id,
            "name": self.action_name,
            "config": self.format_config(),
            "secrets": self.format_secrets(),
        }
        return self.send_api_request(endpoint, "POST", data=data)

    def delete_action(self):
        endpoint = f'actions/connector/{self.action["id"]}'
        return self.send_api_request(endpoint, "DELETE")


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            action_name=dict(type="str"),
            action_type=dict(type="str", choices=["Email", "Webhook"]),  # only the listed choices have been implemented
            config=dict(type="dict"),
            secrets=dict(type="dict", no_log=True),
        )
    )

    argument_dependencies = [("state", "present", ("action_name", "action_type", "config"))]

    results = {"changed": False}

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=argument_dependencies,
        supports_check_mode=True,
    )
    state = module.params.get("state")

    kibana_action = KibanaAction(module)

    if state == "present":
        if kibana_action.action:
            results["msg"] = f"action named {kibana_action.action_name} exists"
            results["action"] = kibana_action.action
            module.exit_json(**results)
        results["changed"] = True
        results["msg"] = f"action named {kibana_action.action_name} will be created"
        if not module.check_mode:
            results["action"] = kibana_action.create_action()
            results["msg"] = f"action named {kibana_action.action_name} created"
        module.exit_json(**results)
    if state == "absent":
        if not kibana_action.action:
            results["msg"] = f"action named {kibana_action.action_name} does not exist"
            module.exit_json(**results)
        results["changed"] = True
        results["msg"] = f"action named {kibana_action.action_name} will be deleted"
        if not module.check_mode:
            kibana_action.delete_action()
        module.exit_json(**results)


if __name__ == "__main__":
    main()
