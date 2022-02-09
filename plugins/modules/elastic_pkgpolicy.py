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
module: elastic_pkgpolicy
short_description: Configure Elastic package policy
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Configure Elastic package policy.
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
  pkg_policy_name:
    description:
    - The name of the package policy
    type: str
    required: true
  pkg_policy_desc:
    description:
    - The description for the package policy
    type: str
  namespace:
    description:
    - The namespace for the agent policy
    type: str
    default: default
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Create Integration Package Policy
  expedient.elastic.elastic_pkgpolicy:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    agent_policy_id: '{{ agent_policy_id }}'
    integration_name: '{{ integration_name }}'
    pkg_policy_name: '{{ pkg_policy_name }}'
    pkg_policy_desc: '{{ pkg_policy_desc }}'
    namespace: '{{ namespace }}'
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
    sample: No Integration Package found, Package Policy created
integration_status:
    description: Agent policy status.
    returned: integration changed
    type: str
    sample: Integration name is not a valid
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
            state=dict(type="str", default="present", choices=["present"]),
            agent_policy_name=dict(type="str"),
            agent_policy_id=dict(type="str"),
            integration_name=dict(type="str", required=True),
            pkg_policy_name=dict(type="str", required=True),
            pkg_policy_desc=dict(type="str"),
            namespace=dict(type="str", default="default"),
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
    pkg_policy_name = module.params.get("pkg_policy_name")
    pkg_policy_desc = module.params.get("pkg_policy_desc")
    integration_name = module.params.get("integration_name")
    namespace = module.params.get("namespace")

    if module.check_mode:
        results["changed"] = False
    else:
        results["changed"] = True

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

    if module.params.get("integration_name"):
        integration_object = kibana.check_integration(integration_name)
    else:
        results["integration_status"] = "No Integration Name provided to get the integration object"
        results["changed"] = False
        module.exit_json(**results)

    if not integration_object:
        results["integration_status"] = "Integration name is not a valid"
        results["changed"] = False
        module.exit_json(**results)

    if state == "present":
        pkg_policy_object = kibana.get_pkg_policy(integration_name, agent_policy_id)
        if pkg_policy_object:
            results["pkg_policy_status"] = "Integration Package found, No package created"
            results["changed"] = False
        else:
            pkg_policy_object = kibana.create_pkg_policy(
                pkg_policy_name,
                pkg_policy_desc,
                agent_policy_id,
                integration_object,
                namespace,
            )
            results["pkg_policy_status"] = "No Integration Package found, Package Policy created"
        results["pkg_policy_object"] = pkg_policy_object

    module.exit_json(**results)


if __name__ == "__main__":
    main()
