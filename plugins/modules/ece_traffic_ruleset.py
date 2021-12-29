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
module: ece_traffic_ruleset
short_description: Placeholder
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description: Placeholder description.
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the traffic ruleset
    type: str
    choices:
    - present
    - update
    - absent
    default: present
  name:
    description:
    - Name of the ruleset
    type: str
    required: true
  description:
    description:
    - Description of the ruleset
    type: str
    default: Ansible created rule
  rules:
    description:
    - List of rules in ruleset
    type: list
    elements: str
    required: true
  associations:
    description:
    - List of associations
    type: list
    elements: str
  ignore_associations:
    description:
    - Dictionary of ignored associations
    type: str
    default: 'False'
extends_documentation_fragment:
- expedient.elastic.ece.documentation
"""

EXAMPLES = """
- name: ECE Traffic Ruleset
  expedient.elastic.ece_traffic_ruleset:
    host: '{{ ece_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    name: Example
    description: Testing
    rules:
    - This is a test
    associations:
    - Placeholder list
    ignore_associations:
      placeholder: needs_data_from_example
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: cluster is up to date
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.expedient.elastic.plugins.module_utils.ece import (
        ECE,
        ece_argument_spec,
    )
except ImportError:
    import sys
    import os

    util_path = new_path = f"{os.getcwd()}/plugins/module_utils"
    sys.path.append(util_path)
    from ece import ECE, ece_argument_spec


class ECE_Traffic_Ruleset(ECE):
    def __init__(self, module):
        super().__init__(module)
        self.rule_name = self.module.params.get("name")
        self.description = self.module.params.get("description")
        self.rules = self.module.params.get("rules")
        self.associations = self.module.params.get("associations")
        self.ignore_associations = self.module.params.get("ignore_associations")

        self.ruleset = self.get_traffic_ruleset_by_name(self.rule_name, include_associations=True)

    def create_ruleset(self):
        endpoint = "deployments/ip-filtering/rulesets"
        data = {
            "name": self.rule_name,
            "description": self.description,
            "rules": self.rules,
        }

        if self.associations:
            # This ensures that the clusters being associated with the ruleset actually exist before trying to add them
            if not self.validate_assocations():
                self.module.fail_json(changed=False, msg=f"cluster {self.associations} does not exist")
            data["associations"] = [
                {
                    "entity_type": "cluster",  # As far as I can tell this is always "cluster" for anything configurable in the Cloud UI
                    "id": self.get_cluster_by_name(association)["cluster_id"],
                }
                for association in self.associations
            ]

        response = self.send_api_request(endpoint, "POST", data=data)
        return response["id"]

    def update_ruleset(self, associations, rules):
        endpoint = f'deployments/ip-filtering/rulesets/{self.ruleset["id"]}'
        pass

    def check_associations(self):
        return [x for x in self.associations if x not in [y["cluster_name"] for y in self.get_cluster_by_id([z["id"] for z in self.ruleset["associations"]])]]

    def check_rules(self):
        return [x for x in self.rules if x not in [y["source"] for y in self.ruleset["rules"]]]

    def validate_assocations(self):
        for association in self.associations:
            if not self.get_cluster_by_name(association):
                return False
        return True

    def delete_ruleset(self):
        endpoint = f'deployments/ip-filtering/rulesets/{self.ruleset["id"]}?ignore_associations={self.ignore_associations}'
        response = self.send_api_request(endpoint, "DELETE")
        return response


def main():
    module_args = ece_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "update", "absent"]),
            name=dict(type="str", required=True),
            description=dict(type="str", default="Ansible created rule"),
            rules=dict(type="list", elements="str", required=True),
            associations=dict(type="list", elements="str"),
            ignore_associations=dict(type="str", default="False"),
        )
    )

    results = {"changed": False}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    state = module.params.get("state")
    ece_traffic_ruleset = ECE_Traffic_Ruleset(module)

    if state == "present":
        if ece_traffic_ruleset.ruleset:
            results["msg"] = f"ruleset {ece_traffic_ruleset.rule_name} exists"
            module.exit_json(**results)
        results["changed"] = True
        if not module.check_mode:
            results["ruleset_id"] = ece_traffic_ruleset.create_ruleset()
        module.exit_json(**results)

    if state == "update":
        if not ece_traffic_ruleset.ruleset:
            results["msg"] = f"ruleset {ece_traffic_ruleset.rule_name} does not exist"
            module.fail_json(**results)

        associations_to_add = []
        rules_to_add = []
        if module.params.get("associations"):
            if not ece_traffic_ruleset.validate_assocations():
                results["msg"] = "one or more clusters being associated do not exist"
            associations_to_add = ece_traffic_ruleset.check_associations()
            results["msg"] = f"the following associations will be added to the ruleset - {associations_to_add}"
        if module.params.get("rules"):
            rules_to_add = ece_traffic_ruleset.check_rules()
            results["msg"] = f"the following rules will be added to the ruleset - {associations_to_add}"

        if len(rules_to_add) == 0 and len(associations_to_add) == 0:
            results["msg"] = "cluster is up to date"
            module.exit_json(**results)

        results["changed"] = True
        if module.check_mode:
            module.exit_json(**results)
        ece_traffic_ruleset.update_ruleset(associations_to_add, rules_to_add)

    if state == "absent":
        if not ece_traffic_ruleset:
            results["msg"] = f"ruleset {ece_traffic_ruleset.rule_name} does not exist"
            module.exit_json(**results)
        results["changed"] = True
        if not module.check_mode:
            ece_traffic_ruleset.delete_ruleset()
        module.exit_json(**results)


if __name__ == "__main__":
    main()
