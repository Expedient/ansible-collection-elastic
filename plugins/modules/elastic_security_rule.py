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
module: elastic_security_rule
short_description: Elastic security rule
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Elastic security rule.
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the module
    choices:
    - present
    default: present
    type: str
  connector_name:
    description:
    - Connector name
    type: str
    required: true
  rule_name:
    description:
    - Rule name
    type: str
    required: true
  action_body:
    description:
    - Body of action
    type: str
  action_group:
    description:
    - Group of action
    type: str
  replace_or_append:
    description:
    - Replace or append rule
    type: str
  existing_actions:
    description:
    - Existing actions
    type: str
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Elastic Role Mapping
  expedient.elastic.elastic_security_rule:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    connector_name: Example
    rule_name: this is an example
    action_body: example_body
    action_group: example_group
    replace_or_append: append
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: rule named test exists
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana, kibana_argument_spec
except ImportError:
    import sys
    import os

    util_path = new_path = f"{os.getcwd()}/plugins/module_utils"
    sys.path.append(util_path)
    from kibana import Kibana, kibana_argument_spec

results = {}


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present"]),
            connector_name=dict(type="str", required=True),
            rule_name=dict(type="str", required=True),
            action_body=dict(type="str"),
            action_group=dict(type="str"),
            replace_or_append=dict(type="str"),
            existing_actions=dict(type="str"),
        )
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True, required_together=[["action_body", "action_group", "replace_or_append"]])
    kibana = Kibana(module)
    results["changed"] = False
    connector_name = module.params.get("connector_name")
    rule_name = module.params.get("rule_name")
    action_body = module.params.get("action_body")
    action_group = module.params.get("action_group")
    replace_or_append = module.params.get("replace_or_append")
    state = module.params.get("state")

    if state == "present":
        connector_exists = kibana.get_alert_connector_by_name(connector_name)
        if not connector_exists:
            results["msg"] = f"action named {connector_name} does not exist"
            results["connector_status"] = "Connector does not exist, exiting"
            results["connector_object"] = connector_exists
            module.exit_json(**results)
        else:
            results["msg"] = f"action named {connector_name} exists"
            results["connector_status"] = "Connector exists by that name"
            results["connector_object"] = connector_exists

        rule_exists = kibana.get_security_rules_byfilter(rule_name)
        target_rule = ""
        for rule in rule_exists["data"]:
            if str(rule["name"]).upper() == str(rule_name).upper():
                target_rule = rule
                break

        if not target_rule:
            results["msg"] = f"rule named {rule_name} does not exist"
            results["rule_status"] = "Rule does not exist, exiting"
            results["rule_object"] = target_rule
            module.exit_json(**results)
        else:
            results["msg"] = f"rule named {rule_name} exists"
            results["rule_status"] = "Rule exists by that name"
            results["rule_object"] = target_rule

        existing_actions = target_rule["actions"]
        rule_action_object = kibana.enable_security_rule_action(
            target_rule["id"], connector_exists["id"], connector_exists["connector_type_id"], action_body, replace_or_append, existing_actions, action_group
        )
        results["changed"] = False
        results["rule_action_status"] = "Created Rule Action Connector"
        results["rule_action_object"] = rule_action_object

    module.exit_json(**results)


if __name__ == "__main__":
    main()
