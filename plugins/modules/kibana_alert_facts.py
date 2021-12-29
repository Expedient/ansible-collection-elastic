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
module: kibana_alert_facts
short_description: get info on a kibana alert
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description:
- This module gets facts about kibana alerts
version_added: 1.0.0
options:
  alert_name:
    description:
    - name of the alert to create
    required: true
    type: str
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: Get Elastic Info for Test Deployment
  expedient.elastic.kibana_alert_facts:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    alert_name: test
  delegate_to: localhost
"""

RETURN = """
alert_config:
    description: Alert Configuration
    returned: always
    type: dict
    sample: {}
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


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            alert_name=dict(type="str", required=True),
        )
    )

    results = {"changed": False}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    kibana = Kibana(module)
    results["alert_config"] = kibana.get_alert_by_name(module.params.get("alert_name"))
    module.exit_json(**results)


if __name__ == "__main__":
    main()
