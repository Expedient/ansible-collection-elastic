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
DOCUMENTATION = """

module: elastic_expedient_security_rules

author: Ian Scott

short_description: Update Security rules to the Expedient Standard

description: 
  - Update Security rules to the Expedient Standard

requirements:
  - python3

options:
      host: 
        description:
          - ECE Host or Deployment Host
        required: true
      port: 
        description:
          - ECE Port or Deployment Port
        required: true      
      username: 
        description:
          - ECE Username or Deployment Username
        required: true    
      password: 
        description:
          - ECE Password or Deployment Password
        required: true    
      deployment_info: 
        description:
          - (when using ECE host:port and credentials)
        required: true    
        deployment_id:
          description: 
          - Deployment ID
          - Required if deployment_name is blank
          type: str
        deployment_name:
          description: 
          - Name of Deployment
          - Required if deployment_id is blank
          type: str  
        resource_type: 
          description:
            - kibana
          required: true    
        ref_id: 
          description:
            - REF ID for kibana cluster, most likely main-kibana
          required: true    
        version: 
          description:
            - Deployment Kibana Version
          required: true
      security_rule_items: 
        description:
          - List of Endpoint Exceptions in JSON format
        required: true  
"""
from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule

try:
    from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
    import sys
    import os

    util_path = new_path = f"{os.getcwd()}/plugins/module_utils"
    sys.path.append(util_path)
    from kibana import Kibana

results = {}


def main():
    module_args = dict(
        host=dict(type="str", required=True),
        port=dict(type="int", default=9243),
        username=dict(type="str", required=True),
        password=dict(type="str", no_log=True, required=True),
        verify_ssl_cert=dict(type="bool", default=True),
        deployment_info=dict(type="dict", default=None),
        security_rule_items=dict(type="list", default=None),
    )
    argument_dependencies = []
    # ('state', 'present', ('enabled', 'alert_type', 'conditions', 'actions')),
    # ('alert-type', 'metrics_threshold', ('conditions'))

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    results["changed"] = False
    security_rule_exception_items = module.params.get("security_rule_items")

    kibana = Kibana(module)

    exception_lists = kibana.get_security_exception_list()
    target_object = None

    for exception_list in exception_lists:
        if exception_list["list_id"] == "endpoint_list":
            target_object = exception_list
            break

    if not target_object:
        results["exception_list_status"] = "endpoint_list was not found"
        results["changed"] = False
        module.fail_json(**results)

    if target_object:
        results["exception_list_status"] = "endpoint_list found"
        results["exception_list_object"] = target_object
        endpoint_list_items = kibana.get_security_exception_list_item()
        results["exception_list_item_object"] = endpoint_list_items

    if not endpoint_list_items:
        results[
            "exception_list_item_status"
        ] = "INFO: Endpoint Security has no entries, that's ok, we will create one"
    else:
        for security_rule_exception_item in security_rule_exception_items:
            for endpoint_list_item in endpoint_list_items:
                if (
                    endpoint_list_item["name"].upper()
                    == security_rule_exception_item["name"].upper()
                ):
                    endpoint_list_item_delete = (
                        kibana.delete_security_exception_list_items(
                            item_id=endpoint_list_item["item_id"]
                        )
                    )
                    results["endpoint_list_item_delete"] = endpoint_list_item_delete
            endpoint_list_item_update = kibana.create_security_exception_list_items(
                id="endpoint_list", body=security_rule_exception_item
            )
            results[
                "endpoint_list_item_update_object_"
                + security_rule_exception_item["name"]
            ] = endpoint_list_item_update

    module.exit_json(**results)


if __name__ == "__main__":
    main()
