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
module: elastic_integration_info
short_description: Returns Elastic integration information by name
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Returns Elastic integration information by name.
version_added: 1.3.0
options:
  integration_name:
    description:
    - The name of the integration
    type: str
    required: true
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Show Integration Package Policy
  expedient.elastic.elastic_integration_info:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    integration_name: '{{ integration_name }}'
"""

RETURN = """
integration_object:
    description: Integration object.
    returned: always
    type: str
    sample: Integration Package found
integration_status:
    description: Agent policy status.
    returned: always
    type: str
    sample: No Integration Name provided to get the integration object
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


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            integration_name=dict(type="str", required=True),
        )
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results["changed"] = False

    integration_name = module.params.get("integration_name")

    kibana = Kibana(module)

    integration_object = kibana.check_integration(integration_name)

    if not integration_object:
        results["integration_status"] = "Integration name is not a valid"
        results["changed"] = False
        module.exit_json(**results)

    integration_object = kibana.check_integration(integration_name)

    if integration_object:
        results["integration_status"] = "Integration Package found"
        results["integration_object"] = integration_object
    else:
        results["integration_status"] = "Integration Package NOT found"

    results["integration_object"] = integration_object

    module.exit_json(**results)


if __name__ == "__main__":
    main()
