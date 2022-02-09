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

from ansible.module_utils.urls import open_url
from json import loads, dumps
from urllib.error import HTTPError
from urllib.parse import quote


def kibana_argument_spec():
    return dict(
        host=dict(type="str", required=True),
        port=dict(type="str", required=False, default="9243"),
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", required=False, default=True, aliases=["verify_ssl_cert"]),
    )


class Kibana(object):
    def __init__(self, module):
        self.module = module
        self.host = module.params.get("host")
        self.port = module.params.get("port")
        self.username = module.params.get("username")
        self.password = module.params.get("password")
        self.validate_certs = module.params.get("validate_certs")
        self.version = None  # this allows the first request to get the cluster version without erroring out
        self.version = self.get_cluster_version()

    def send_api_request(self, endpoint, method, data=None):
        url = f"https://{self.host}:{self.port}/api/{endpoint}"
        headers = {}
        payload = None
        if data:
            headers["Content-Type"] = "application/json"
            payload = dumps(data)
        if self.version:
            headers["kbn-version"] = self.version
        try:
            response = open_url(
                url,
                data=payload,
                method=method,
                validate_certs=self.validate_certs,
                headers=headers,
                force_basic_auth=True,
                url_username=self.username,
                url_password=self.password,
                timeout=60,
            )
        except HTTPError as e:
            raise e  # This allows errors raised during the request to be inspected while debugging
        return loads(response.read())

    def get_cluster_status(self):
        endpoint = "status"
        return self.send_api_request(endpoint, "GET")

    def get_cluster_version(self):
        status = self.get_cluster_status()
        return status["version"]["number"]

    def get_alert_types(self):
        endpoint = "alert/types"
        alert_types = self.send_api_request(endpoint, "GET")
        return alert_types

    def get_alert_by_name(self, alert_name):
        endpoint = f"alerts/_find?search_fields=name&search={quote(alert_name)}"
        alerts = self.send_api_request(endpoint, "GET")
        return next(filter(lambda x: x["name"] == alert_name, alerts["data"]), None)

    def get_alert_connector_by_name(self, connector_name):
        endpoint = "actions/connectors"
        actions = self.send_api_request(endpoint, "GET")
        return next(filter(lambda x: x["name"] == connector_name, actions), None)

    def get_alert_connector_type_by_name(self, connector_type_name):
        endpoint = "actions/connector_types"
        connector_types = self.send_api_request(endpoint, "GET")
        return next(filter(lambda x: x["name"] == connector_type_name, connector_types), None)

    # Elastic Security Rules functions

    def update_security_rule(self, body):
        endpoint = "detection_engine/rules"
        update_rule = self.send_api_request(endpoint, "PATCH", data=body)
        return update_rule

    def get_security_rules(self, page_size, page_no):
        endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size)
        rules = self.send_api_request(endpoint, "GET")
        return rules

    def get_security_rules_byfilter(self, rule_name):
        page_no = 1
        page_size = 100
        filter_scrubbed = quote(str(rule_name))
        endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size) + "&filter=alert.attributes.name:" + filter_scrubbed
        rules = self.send_api_request(endpoint, "GET")
        return rules

    def enable_security_rule(self, rule_id):
        body = {"enabled": True, "id": rule_id}
        update_rule = self.update_security_rule(self, body)
        return update_rule

    def enable_security_rule_action(self, rule_id, action_id, action_type, body, replace_or_append, existing_actions, action_group="default"):
        params = {"body": str(body)}
        action_def = {"action_type_id": action_type, "id": action_id, "group": action_group, "params": params}
        if replace_or_append == "replace":
            body = {"id": rule_id, "throttle": "rule", "actions": [action_def]}
        elif replace_or_append == "append":
            action_def.append(existing_actions)
            body = {"id": rule_id, "actions": [action_def]}
        update_rule = self.update_security_rule(body)
        return update_rule

    def activate_security_rule(self, rule_name):
        # Getting first page of rules
        page_number = 1
        page_size = 100
        rules = self.get_security_rules_byfilter(rule_name)
        noOfRules = rules["total"]
        allrules = rules["data"]
        # Going through each rule page by page and enabling each rule that isn't enabled.
        while noOfRules > page_size * (page_number - 1):
            for rule in allrules:
                if not rule["enabled"] and rule_name == rule["name"]:
                    enable_rule = self.enable_security_rule(rule["id"])
                    return rule["name"] + ": Rule is updated"
                elif rule["enabled"] and rule_name == rule["name"]:
                    return rule["name"] + ": Rule is already enabled"
        return rule["name"] + ": Rule not found"

    # Elastic Integration functions

    def get_integrations(self):
        endpoint = "fleet/epm/packages"
        integration_objects = self.send_api_request(endpoint, "GET")
        return integration_objects

    def install_integration(self, integration_name, version):
        body = {"force": True}
        body_JSON = dumps(body)
        endpoint = "fleet/epm/packages/" + integration_name + "-" + version
        if not self.module.check_mode:
            integration_install = self.send_api_request(endpoint, "POST", data=body_JSON)
        else:
            integration_install = "Cannot proceed with check_mode set to " + self.module.check_mode
        return integration_install

    def check_integration(self, integration_name):
        integration_objects = self.get_integrations()
        integration_response = None
        for integration in integration_objects["response"]:
            if integration["title"].upper() in integration_name.upper():
                if integration["status"] != "installed":
                    integration_install = self.install_integration(integration["name"], integration["version"])
                integration_detail_object = self.get_integration(integration["name"], integration["version"])
                integration_response = integration_detail_object["response"]
                break
        return integration_response

    def get_integration(self, integration_name, version):
        endpoint = "fleet/epm/packages/" + integration_name + "-" + version
        integration_object = self.send_api_request(endpoint, "GET")
        return integration_object

    # Elastic Integration Package Policy functions

    def get_all_pkg_policies(self):
        endpoint = "fleet/package_policies"
        pkgpolicy_objects = self.send_api_request(endpoint, "GET")
        return pkgpolicy_objects

    def update_pkg_policy(self, pkgpolicy_id, body):
        if "id" in body:
            pkgpolicy_id = body["id"]
            body.pop("id")
        if "revision" in body:
            body.pop("revision")
        if "created_at" in body:
            body.pop("created_at")
        if "created_by" in body:
            body.pop("created_by")
        if "updated_at" in body:
            body.pop("updated_at")
        if "updated_by" in body:
            body.pop("updated_by")
        if not self.module.check_mode:
            endpoint = "fleet/package_policies/" + pkgpolicy_id
            pkg_policy_update = self.send_api_request(endpoint, "PUT", data=body)
        else:
            pkg_policy_update = "Cannot proceed with check_mode set to " + self.module.check_mode
        return pkg_policy_update

    def get_pkg_policy(self, integration_name, agent_policy_id):
        pkg_policy_objects = self.get_all_pkg_policies()
        pkg_policy_object = None
        for pkgPolicy in pkg_policy_objects["items"]:
            if pkgPolicy["package"]["title"].upper() == integration_name.upper() and pkgPolicy["policy_id"] == agent_policy_id:
                pkg_policy_object = pkgPolicy
                break
        return pkg_policy_object

    def create_pkg_policy(self, pkg_policy_name, pkg_policy_desc, agent_policy_id, integration_object, namespace="default"):
        pkg_policy_object = self.get_pkg_policy(integration_object["name"], agent_policy_id)
        inputs_body = []
        if "policy_templates" in integration_object:
            for policy_template in integration_object["policy_templates"]:
                if "inputs" in policy_template:
                    if policy_template["inputs"] != None:
                        for policy_input in policy_template["inputs"]:
                            inputs_body_entry = {}
                            inputs_body_entry["policy_template"] = policy_template["name"]
                            inputs_body_entry["enabled"] = True
                            inputs_body_entry["type"] = policy_input["type"]
                            if "config" in policy_input:
                                inputs_body_entry["config"] = policy_input["config"]
                            else:
                                inputs_body_entry["config"] = {}
                            input_body_template_var = {}
                            if "vars" in policy_input:
                                for policy_template_var in policy_input["vars"]:
                                    if "value" in policy_template_var:
                                        input_body_template_var[policy_template_var["name"]] = {
                                            "type": policy_template_var["type"],
                                            "value": policy_template_var["value"],
                                        }
                                    else:
                                        input_body_template_var[policy_template_var["name"]] = {"type": policy_template_var["type"]}
                            inputs_body_entry["vars"] = input_body_template_var
                            inputs_body_streams = []
                            for integration_object_input in integration_object["data_streams"]:
                                inputs_body_stream_entry = {}
                                # inputs_body_stream_entry['enabled'] = True
                                for integration_input_stream in integration_object_input["streams"]:
                                    if "enabled" in integration_input_stream:
                                        inputs_body_stream_entry["enabled"] = integration_input_stream["enabled"]
                                    else:
                                        inputs_body_stream_entry["enabled"] = False
                                    if integration_input_stream["input"] == policy_input["type"]:
                                        inputs_body_streams_datastream = {}
                                        inputs_body_streams_datastream["dataset"] = integration_object_input["dataset"]
                                        inputs_body_streams_datastream["type"] = integration_object_input["type"]
                                        inputs_body_stream_entry["data_stream"] = inputs_body_streams_datastream
                                        input_body_stream_var = {}
                                        for integration_stream_var in integration_input_stream["vars"]:
                                            if "default" in integration_stream_var:
                                                input_body_stream_var[integration_stream_var["name"]] = {
                                                    "type": integration_stream_var["type"],
                                                    "value": integration_stream_var["default"],
                                                }
                                            else:
                                                input_body_stream_var[integration_stream_var["name"]] = {"type": integration_stream_var["type"], "value": ""}
                                        inputs_body_stream_entry["vars"] = input_body_stream_var
                                        inputs_body_streams.append(inputs_body_stream_entry)

                                inputs_body_entry["streams"] = inputs_body_streams
                            inputs_body.append(inputs_body_entry)

        if not pkg_policy_object:
            body = {
                "name": pkg_policy_name,
                "namespace": namespace.lower(),
                "description": pkg_policy_desc,
                "enabled": True,
                "policy_id": agent_policy_id,
                "output_id": "",
                "inputs": inputs_body,
                "package": {"name": integration_object["name"], "title": integration_object["title"], "version": integration_object["version"]},
            }
            body_JSON = dumps(body)
            endpoint = "fleet/package_policies"
            if not self.module.check_mode:
                pkg_policy_object = self.send_api_request(endpoint, "POST", data=body_JSON)
            else:
                pkg_policy_object = "Cannot proceed with check_mode set to " + self.module.check_mode
        return pkg_policy_object

    def toggle_pkg_policy_input_onoff(self, pkg_policy_object, type, onoff):
        pkg_policy_object_updated = pkg_policy_object
        i = 0
        for input in pkg_policy_object["inputs"]:
            if input["type"] == type:
                pkg_policy_object_updated["inputs"][i]["enabled"] = onoff
            i = i + 1
        return pkg_policy_object_updated

    def toggle_pkg_policy_stream_onoff(self, pkg_policy_object, dataset, onoff):
        pkg_policy_object_updated = pkg_policy_object
        i = 0
        for input in pkg_policy_object_updated["inputs"]:
            j = 0
            for streams in input["streams"]:
                if "compiled_stream" in streams:
                    pkg_policy_object_updated["inputs"][i]["streams"][j].pop("compiled_stream")
                if streams["data_stream"]["dataset"] == dataset:
                    pkg_policy_object_updated["inputs"][i]["streams"][j]["enabled"] = onoff
                j = j + 1
            i = i + 1
        return pkg_policy_object_updated

    # Elastic Agent Policy functions

    def get_all_agent_policys(self):
        endpoint = "fleet/agent_policies"
        agent_policy_objects = self.send_api_request(endpoint, "GET")
        return agent_policy_objects

    def create_agent_policy(self, agent_policy_id, agent_policy_name, agent_policy_desc, namespace="default"):
        if agent_policy_id:
            agent_policy_object = self.get_agent_policy_byid(agent_policy_id)
        else:
            agent_policy_object = self.get_agent_policy_byname(agent_policy_name)

        if not agent_policy_object:
            body = {"name": agent_policy_name, "namespace": namespace.lower(), "description": agent_policy_desc, "monitoring_enabled": []}
            body_JSON = dumps(body)

            if not self.module.check_mode:
                endpoint = "fleet/agent_policies"
                agent_policy_object = self.send_api_request(endpoint, "POST", data=body_JSON)
                agent_policy_object = agent_policy_object["item"]
            else:
                agent_policy_object = "Cannot proceed with check_mode set to " + self.module.check_mode
        return agent_policy_object

    def get_agent_policy_byname(self, agent_policy_name):
        agent_policy_object = None
        agent_policy_objects = self.get_all_agent_policys()
        for agent_policy in agent_policy_objects["items"]:
            if agent_policy["name"].upper() == agent_policy_name.upper():
                agent_policy_object = agent_policy
                continue
        return agent_policy_object

    def get_agent_policy_byid(self, agent_policy_id):
        endpoint = "fleet/agent_policies/" + agent_policy_id
        agent_policy_object = self.send_api_request(endpoint, "GET")
        return agent_policy_object["item"]

    # Elastic Agent functions

    def get_agent_list(self):
        page_size = 50
        page_number = 1
        endpoint = "fleet/agents?page=" + str(page_number) + "&perPage=" + str(page_size)
        agent_list = self.send_api_request(endpoint, "GET")
        noOfAgents = agent_list["total"]
        agent_list_result = agent_list
        while noOfAgents > page_size * (page_number - 1):
            agent_no = 0
            endpoint = "fleet/agents?page=" + str(page_number) + "&perPage=" + str(page_size)
            agent_list_page = self.send_api_request(endpoint, "GET")
            while agent_no < len(agent_list_page["list"]):
                agent_list_result["list"].append(agent_list_page["list"][agent_no])
                agent_no = agent_no + 1
            page_number = page_number + 1
        return agent_list_result
