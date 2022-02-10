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
module: elastic_agentpolicy
short_description: Configures Elastic agent policy
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Configures Elastic agent policy.
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
  agent_policy_desc:
    description:
    - The description for the agent policy
    type: str
    default: None
  namespace:
    description:
    - The namespace for the agent policy
    type: str
    default: default
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Create Agent Policy
  expedient.elastic.elastic_agentpolicy:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    agent_policy_name: '{{ agent_policy_name }}'
    agent_policy_desc: '{{ agent_policy_desc }}'
    namespace: '{{ namespace }}'
"""

RETURN = """
agent_policy_status:
    description: Agent policy status.
    returned: always
    type: str
    sample: Agent Policy created
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
            agent_policy_desc=dict(type="str", default="None"),
            namespace=dict(type="str", default="default"),
        )
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("agent_policy_name", "agent_policy_id")],
        required_one_of=[("agent_policy_name", "agent_policy_id")],
    )

    kibana = Kibana(module)
    state = module.params.get("state")
    agent_policy_name = module.params.get("agent_policy_name")
    agent_policy_desc = module.params.get("agent_policy_desc")
    agent_policy_id = module.params.get("agent_policy_id")
    namespace = module.params.get("namespace")

    if module.check_mode:
        results["changed"] = False
    else:
        results["changed"] = True

    if state == "present":
        agent_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
        if agent_policy_object:
            results["agent_policy_status"] = "Agent Policy already exists"
            results["changed"] = False
        else:
            agent_policy_object = kibana.create_agent_policy(agent_policy_id, agent_policy_name, agent_policy_desc, namespace)
            results["agent_policy_status"] = "Agent Policy created"
        results["agent_policy_object"] = agent_policy_object
    else:
        results["agent_policy_status"] = "A valid state was not passed"

    module.exit_json(**results)


if __name__ == "__main__":
    main()
