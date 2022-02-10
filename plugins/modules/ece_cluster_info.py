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
module: ece_cluster_info
short_description: Return ECE cluster information
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description:
- Return ECE cluster information.
version_added: 1.0.0
options:
  deployment_name:
    description:
    - The name of the desired ECE deployment
    required: true
    type: str
extends_documentation_fragment:
- expedient.elastic.ece.documentation
"""

EXAMPLES = """
- name: Get Elastic Info for Test Deployment
  expedient.elastic.ece_cluster_info:
    host: '{{ ece_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    deployment_name: test
  delegate_to: localhost
"""

RETURN = """
deployment_kibana_endpoint:
    description: Kibana Endpoint
    returned: always
    type: str
    sample: test-instance.elastic.expedient.cloud
deployment_kibana_url:
    description: Kibana URL
    returned: always
    type: str
    sample: https://test-instance.elastic.expedient.cloud:9243
"""

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

results = {}


def main():
    module_args = ece_argument_spec()
    module_args.update(dict(deployment_name=dict(type="str", required=True)))

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    deployment_name = module.params.get("deployment_name")

    ElasticDeployments = ECE(module)
    deployment_kibana_info = ElasticDeployments.get_deployment_kibana_info(deployment_name)

    if not deployment_kibana_info:
        results["deployment_kibana_endpoint"] = None
        results["deployment_kibana_url"] = None
        results["deployment_kibana_info"] = "No deployment kibana was returned, check your deployment name"
    else:
        results["deployment_kibana_endpoint"] = (
            deployment_kibana_info["info"]["metadata"].get("aliased_endpoint") or deployment_kibana_info["info"]["metadata"]["endpoint"]
        )
        results["deployment_kibana_url"] = deployment_kibana_info["info"]["metadata"]["aliased_url"]
        results["deployment_kibana_info"] = "Deployment kibana was returned sucessfully"

    results["changed"] = False
    module.exit_json(**results)


if __name__ == "__main__":
    main()
