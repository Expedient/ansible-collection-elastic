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
module: elastic_endpoint_security
short_description: Configure Elastic Endpoint Security
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Configure Elastic Endpoint Security.
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the module
    choices:
    - present
    default: present
    type: str
  agent_policy_name:
    description:
    - The name of the agent policy
    - Required if C(agent_policy_id) is not provided
    type: str
  agent_policy_id:
    description:
    - The id of the agent policy
    - Required if C(agent_policy_name) is not provided
    type: str
  integration_name:
    description:
    - The name of the integration
    type: str
    required: true
  pkg_policy_name:
    description:
    - The name of the package policy
    type: str
    required: true
  pkg_policy_desc:
    description:
    - The description of the package policy
    type: str
  namespace:
    description:
    - The namespace for the agent policy
    type: str
    default: default
  integration_settings:
    description:
    - Integration Settings
    type: dict
  prebuilt_rules_activate:
    description:
    - Prebuild rules activate
    type: bool
    default: true
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Create Integration Package - System
  expedient.elastic.elastic_endpoint_security:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    agent_policy_id: '{{ agent_policy_id }}'
    integration_name: System
    pkg_policy_name: system-1
    pkg_policy_desc: system-1
    namespace: '{{ namespace }}'
"""

RETURN = """
agent_policy_status:
    description: Agent Policy found.
    returned: always
    type: str
    sample: Agent Policy found.
pkg_policy_status:
    description: No Integration Package found, Package Policy created.
    returned: always
    type: str
    sample: Integration Package found
updated_pkg_policy_info:
    description: Updated package policy information.
    returned: changed
    type: str
    sample: 'Endpoint Security: Rule is already enabled'
"""

from ansible.module_utils.basic import AnsibleModule

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

results = {}


class SecurityBaseline(Kibana):
    def __init__(self, module):
        super().__init__(module)
        self.module = module
        self.integration_pkg_name = module.params.get("integration_pkg_name")
        self.integration_pkg_desc = module.params.get("integration_pkg_desc")
        self.prebuilt_rules_activate = module.params.get("prebuilt_rules_activate")
        self.agent_policy_name = module.params.get("agent_policy_name")
        self.agent_policy_desc = module.params.get("agent_policy_desc")
        self.pkg_policy_name = module.params.get("pkg_policy_name")
        self.pkg_policy_desc = module.params.get("pkg_policy_desc")
        self.integration_settings = self.module.params.get("integration_settings")

    def create_securityctrl_baseline_settings(self, pkg_policy_object):
        # Checking and creating package policy associated with Integration

        if "package" not in pkg_policy_object:
            pkg_policy_object = pkg_policy_object["item"]
        pkg_policy_object_id = pkg_policy_object["id"]

        if self.module.check_mode:
            results["pkg_policy_update_status"] = "Check mode is set to True, not going to update pkg policy"
        elif self.integration_settings:
            integration_settings_json = self.integration_settings
            results["passed_integration_settings"] = integration_settings_json
            if "name" not in integration_settings_json:
                integration_settings_json["name"] = pkg_policy_object["name"]
            if "policy_id" not in integration_settings_json:
                integration_settings_json["policy_id"] = pkg_policy_object["policy_id"]
            if "enabled" not in integration_settings_json:
                integration_settings_json["enabled"] = pkg_policy_object["enabled"]
            if "namespace" not in integration_settings_json:
                integration_settings_json["namespace"] = pkg_policy_object["namespace"]
            if "package" not in integration_settings_json:
                integration_settings_json["package"] = pkg_policy_object["package"]
            if "output_id" not in integration_settings_json:
                integration_settings_json["output_id"] = pkg_policy_object["output_id"]
            if "inputs" not in integration_settings_json:
                integration_settings_json["inputs"] = pkg_policy_object["inputs"]
            pkg_policy_info = self.update_pkg_policy(pkg_policy_object_id, integration_settings_json)
        elif pkg_policy_object["package"]["title"] == "Prebuilt Security Detection Rules" and self.prebuilt_rules_activate and not self.module.check_mode:
            pkg_policy_info = self.activate_security_rule("Endpoint Security")
        else:
            pkg_policy_info = None

        return pkg_policy_info


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present"]),
            agent_policy_id=dict(type="str"),
            agent_policy_name=dict(type="str"),
            integration_name=dict(type="str", required=True),
            pkg_policy_name=dict(type="str", required=True),
            pkg_policy_desc=dict(type="str"),
            namespace=dict(type="str", default="default"),
            prebuilt_rules_activate=dict(type="bool", default=True),
            integration_settings=dict(type="dict"),
        )
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("agent_policy_name", "agent_policy_id")],
        required_one_of=[("agent_policy_name", "agent_policy_id")],
    )

    state = module.params.get("state")
    agent_policy_name = module.params.get("agent_policy_name")
    agent_policy_id = module.params.get("agent_policy_id")
    integration_name = module.params.get("integration_name")
    pkg_policy_name = module.params.get("pkg_policy_name")
    pkg_policy_desc = module.params.get("pkg_policy_desc")
    pkg_policy_desc = module.params.get("pkg_policy_desc")
    namespace = module.params.get("namespace")
    integration_settings = module.params.get("integration_settings")

    if module.check_mode:
        results["changed"] = False
    else:
        results["changed"] = True

    kibana = SecurityBaseline(module)

    if not module.params.get("agent_policy_id"):
        agency_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    else:
        agency_policy_object = kibana.get_agent_policy_byid(agent_policy_id)

    if agency_policy_object:
        agent_policy_id = agency_policy_object.get("id")
        if agent_policy_id:
            results["agent_policy_status"] = "Agent Policy found."
    else:
        results["agent_policy_status"] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
        results["changed"] = False
        module.exit_json(**results)

    if module.params.get("integration_name"):
        integration_object = kibana.check_integration(integration_name)
    else:
        results["integration_status"] = "No Integration Name provided to get the integration object"
        results["changed"] = False
        module.exit_json(**results)

    if not integration_object:
        results["integration_status"] = "Integration name is not valid"
        results["changed"] = False
        module.exit_json(**results)

    if state == "present":
        pkg_policy_object = kibana.get_pkg_policy(integration_name, agent_policy_id)
        if pkg_policy_object:
            results["pkg_policy_status"] = "Integration Package found, No package created"
            results["changed"] = False
        else:
            if not module.check_mode:
                pkg_policy_object = kibana.create_pkg_policy(
                    pkg_policy_name,
                    pkg_policy_desc,
                    agent_policy_id,
                    integration_object,
                    namespace,
                )
                results["pkg_policy_status"] = "No Integration Package found, Package Policy created"
                results["changed"] = True
            else:
                results["pkg_policy_status"] = "No Integration Package found, Package Policy not created becans check_mode is set to true"
                results["changed"] = False

        results["pkg_policy_object"] = pkg_policy_object

    module.exit_json(**results)


if __name__ == "__main__":
    main()
