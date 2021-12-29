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
module: ece_facts
short_description: Return ECE cluster information for all clusters
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description:
- Return ECE cluster information for all clusters.
version_added: 1.0.0
options: {}
extends_documentation_fragment:
- expedient.elastic.ece.documentation
"""

EXAMPLES = """
- name: Get Elastic Facts
  expedient.elastic.ece_facts:
    host: '{{ ece_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
  delegate_to: localhost
"""

RETURN = """
clusters:
    description: Clusters info
    returned: always
    type: dict
    sample: {}
"""

# at the moment this is incredibly limited and exists purely to allow for usage reporting


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


class ECE_Facts(ECE):
    def __init__(self, module):
        super().__init__(module)


def main():
    module_args = ece_argument_spec()

    results = {"changed": False}
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    ece_facts = ECE_Facts(module)

    results["clusters"] = ece_facts.get_clusters()

    module.exit_json(**results)


if __name__ == "__main__":
    main()
