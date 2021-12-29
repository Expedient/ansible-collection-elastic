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
module: elastic_agentpolicy_info
short_description: Returns Elastic agent policy information by id or name
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Returns Elastic agent policy information by id or name.
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
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Get Agent Policy by Name
  expedient.elastic.elastic_agentpolicy_info:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    agent_policy_name: '{{ agent_policy_name }}'
- name: Get Agent Policy by ID
  expedient.elastic.elastic_agentpolicy_info:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    agent_policy_id: '{{ agent_policy_id }}'
"""

RETURN = """
agent_policy_status:
    description: Agent policy status.
    returned: always
    type: str
    sample: Agent Policy found.
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
    module_args.update(dict(agent_policy_name=dict(type="str"), agent_policy_id=dict(type="str")))

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("agent_policy_name", "agent_policy_id")],
        required_one_of=[("agent_policy_name", "agent_policy_id")],
    )

    kibana = Kibana(module)
    results["changed"] = False
    agent_policy_id = module.params.get("agent_policy_id")
    agent_policy_name = module.params.get("agent_policy_name")

    if module.params.get("agent_policy_name"):
        agent_policy_object = kibana.get_agent_policy_byname(agent_policy_name)
    else:
        agent_policy_object = kibana.get_agent_policy_byid(agent_policy_id)

    if agent_policy_object:
        results["agent_policy_status"] = "Agent Policy Found"
        results["agent_policy_object"] = agent_policy_object
    else:
        results["agent_policy_status"] = "No Agent Policy was returned, check your Agent Policy Name"
        results["agent_policy_object"] = None

    module.exit_json(**results)


if __name__ == "__main__":
    main()
