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
module: elastic_agentlist_info
short_description: Returns Elastic agent list information
author: Ian R Scott (@ianrscottexp)
requirements:
- python3
description:
- Returns Elastic agent list information.
version_added: 1.0.0
options: {}
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Agent List
  expedient.elastic.elastic_agentlist_info:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
"""

RETURN = """
agent_list_status:
    description: Agent List status.
    returned: always
    type: str
    sample: Getting Agent List
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

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    kibana = Kibana(module)
    results["changed"] = False

    agent_list = kibana.get_agent_list()

    results["agent_list_status"] = "Getting Agent List"
    results["agent_list_object"] = agent_list

    module.exit_json(**results)


if __name__ == "__main__":
    main()
