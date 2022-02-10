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
module: elastic_user
short_description: elastic user management
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description:
- This module creates or deletes users with elastic
- Update state not yet implemented
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the user
    choices:
    - present
    - absent
    default: present
    type: str
  elastic_user:
    description:
    - The name of the user to create or delete
    type: str
    required: true
  elastic_password:
    description:
    - Password for the user
    - Required when creating a new user
    type: str
    required: false
  roles:
    description:
    - list of roles to assign to the user
    - Required when creating a new user
    type: list
    required: false
    elements: str
  full_name:
    description:
    - full name of the user
    type: str
    required: false
  email:
    description:
    - email address to associate with the user
    type: str
    required: false
  metadata:
    description:
    - metadata object to associate with the user
    - can contain any arbitrary key:value pairs
    type: dict
    default: {}
  enabled:
    description:
    - whether to enable the newly created user
    type: bool
    default: true
extends_documentation_fragment:
- expedient.elastic.elastic.documentation
"""

EXAMPLES = """
- name: Elastic User
  expedient.elastic.elastic_user:
    host: '{{ elastic_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    elastic_user: test_user
    elastic_password: super_secret_password
    roles:
    - super_user
    full_name: Test User for Example
    email: fake_email@email.com
    metadata:
      fake_metadata: need_real_data_here
    enabled: yes
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: User Test exists
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


class ElasticUser(Elastic):
    def __init__(self, module):
        super().__init__(module)
        self.elastic_username = self.module.params.get("elastic_user")
        self.elastic_password = self.module.params.get("elastic_password")
        self.roles = self.module.params.get("roles")
        self.full_name = self.module.params.get("full_name")
        self.email = self.module.params.get("email")
        self.enabled = self.module.params.get("enabled")
        self.metadata = self.module.params.get("metadata")
        self.user_object = self.get_user(self.elastic_username)
        self.user = self.user_object.get(self.elastic_username)

    def create_user(self):
        endpoint = f"_security/user/{self.elastic_username}"
        data = {
            "password": self.elastic_password,
            "roles": self.roles,
            "full_name": self.full_name,
            "email": self.email,
            "metadata": self.metadata,
            "enabled": self.enabled,
        }
        return self.send_api_request(endpoint, data=data, method="POST")

    def delete_user(self):
        endpoint = f"_security/user/{self.elastic_username}"
        return self.send_api_request(endpoint, method="DELETE")


def main():
    module_args = elastic_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            elastic_user=dict(type="str", required=True),
            elastic_password=dict(type="str", required=False, no_log=True),
            roles=dict(type="list", elements="str"),
            full_name=dict(type="str", required=False),
            email=dict(type="str", required=False),
            metadata=dict(type="dict"),
            enabled=dict(type="bool", default=True),
        )
    )

    results = {"changed": False}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    state = module.params.get("state")
    elastic_user = ElasticUser(module)

    if state == "present":
        if elastic_user.user:
            results["msg"] = f'user {elastic_user.user["username"]} exists'
            module.exit_json(**results)
        results["operation_result"] = elastic_user.create_user()
        module.exit_json(**results)

    if state == "absent":
        if not elastic_user.user:
            results["msg"] = f'user {module.params.get("elastic_user")} does not exist'
        results["operation_result"] = elastic_user.delete_user()
        module.exit_json(**results)


if __name__ == "__main__":
    main()
