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
module: elastic_role_mapping
short_description: Elastic role mapping
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Elastic role mapping.
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the module
    choices:
    - present
    default: present
    type: str
  name:
    description:
    - Name of the role mapping
    type: str
    required: true
  enabled:
    description:
    - Role mapping enabled
    type: bool
    default: true
  roles:
    description:
    - Roles
    type: list
    required: true
    elements: str
  rules:
    description:
    - Rules
    type: dict
    required: true
  metadata:
    description:
    - Metadata
    type: dict
extends_documentation_fragment:
- expedient.elastic.elastic.documentation
"""

EXAMPLES = """
- name: Elastic Role Mapping
  expedient.elastic.elastic_role_mapping:
    host: '{{ elastic_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    name: Example
    enabled: yes
    roles:
    - example_list
    rules:
      example_rule: need_real_data_here
    metadata:
      example_metadata: need_real_data_here
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: role mapping test exists
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.expedient.elastic.plugins.module_utils.elastic import (
        Elastic,
        elastic_argument_spec,
    )
except ImportError:
    import sys
    import os

    util_path = new_path = f"{os.getcwd()}/plugins/module_utils"
    sys.path.append(util_path)
    from elastic import Elastic, elastic_argument_spec


class ElasticRoleMapping(Elastic):
    def __init__(self, module):
        super().__init__(module)
        self.role_mapping_name = self.module.params.get("name")
        self.enabled = self.module.params.get("enabled")
        self.roles = self.module.params.get("roles")
        self.rules = self.module.params.get("rules")
        self.role_mapping = self.get_role_mapping(self.role_mapping_name)

    def create_role_mapping(self):
        endpoint = f"_security/role_mapping/{self.role_mapping_name}"
        data = {
            "enabled": self.enabled,
            "roles": self.roles,
            "rules": self.rules,
            "metadata": self.metadata,
        }
        self.send_api_request(endpoint, data=data, method="POST")


def main():
    module_args = elastic_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present"]),
            name=dict(type="str", required=True),
            enabled=dict(type="bool", default=True),
            roles=dict(type="list", required=True, elements="str"),
            rules=dict(type="dict", required=True),
            metadata=dict(type="dict"),
        )
    )

    results = {"changed": False}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    state = module.params.get("state")
    role_mapping = ElasticRoleMapping(module)

    if state == "present":
        if role_mapping.role_mapping:
            results["msg"] = f"role mapping {role_mapping.role_mapping_name} exists"
            results["role_mapping"] = role_mapping.role_mapping
        else:
            results["changed"] = True
            results["msg"] = f"creating role mapping {role_mapping.role_mapping_name}"
            results["role_mapping"] = role_mapping.create_role_mapping()

    module.exit_json(**results)


if __name__ == "__main__":
    main()
