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
module: elastic_pkgpolicy_info
short_description: Returns Elastic package policy information by name
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Returns Elastic package policy information by name.
version_added: 1.0.0
options:
  agent_policy_name:
    description:
    - The name of the agent policy to return
    - Required if C(agent_policy_id) is not provided
    type: str
  agent_policy_id:
    description:
    - The id of the agent policy to return
    - Required if C(agent_policy_name) is not provided
    type: str
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
  expedient.elastic.elastic_pkgpolicy_info:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    agent_policy_id: '{{ agent_policy_id }}'
    integration_name: '{{ integration_name }}'
"""

RETURN = """
agent_policy_status:
    description: Agent policy status.
    returned: always
    type: str
    sample: Agent Policy found.
pkg_policy_status:
    description: Package policy status.
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
            agent_policy_name=dict(type="str"),
            agent_policy_id=dict(type="str"),
            integration_name=dict(type="str", required=True),
        )
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("agent_policy_name", "agent_policy_id")],
        required_one_of=[("agent_policy_name", "agent_policy_id")],
    )

    results["changed"] = False

    agent_policy_name = module.params.get("agent_policy_name")
    agent_policy_id = module.params.get("agent_policy_id")
    integration_name = module.params.get("integration_name")

    kibana = Kibana(module)

    if module.params.get("agent_policy_id"):
        agency_policy_object = kibana.get_agent_policy_byid(agent_policy_id)
    else:
        agency_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    if agency_policy_object:
        agent_policy_id = agency_policy_object.get("id")
        results["agent_policy_status"] = "Agent Policy found."
    else:
        results["agent_policy_status"] = "Agent Policy was not found. Cannot continue without valid Agent Policy Name or ID"
        results["changed"] = False
        module.exit_json(**results)

    if integration_name:
        integration_object = kibana.check_integration(integration_name)
    else:
        results["integration_status"] = "No Integration Name provided to get the integration object"
        results["changed"] = False
        module.exit_json(**results)

    if not integration_object:
        results["integration_status"] = "Integration name is not a valid"
        results["changed"] = False
        module.exit_json(**results)

    pkg_policy_object = kibana.get_pkg_policy(integration_name, agent_policy_id)

    if pkg_policy_object:
        results["pkg_policy_status"] = "Integration Package found"
        results["pkg_policy_object"] = pkg_policy_object
    else:
        results["pkg_policy_status"] = "Integration Package NOT found"

    results["pkg_policy_object"] = pkg_policy_object

    module.exit_json(**results)


if __name__ == "__main__":
    main()
