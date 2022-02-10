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
module: kibana_alert
short_description: Create or delete alerts in Kibana
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
description:
- This module creates or deletes alerts in kibana
- currently supports threshold alerts
version_added: 1.0.0
options:
  state:
    description:
    - setting whether alert should be created or deleted
    choices: [present, absent]
    default: present
    type: str
  alert_name:
    description:
    - name of the alert to create
    required: true
    type: str
  alert_type:
    description:
    - Alert Type
    type: str
    choices:
    - metrics_threshold
  enabled:
    description:
    - whether to enable the alert when creating
    default: true
    type: bool
  tags:
    description:
    - metadata tags to attach to the alert
    type: list
    elements: str
  check_every:
    description:
    - frequency to check the alert on
    default: 1m
    type: str
  notify_on:
    description:
    - when to send the alert
    default: status_change
    choices:
    - status_change
    type: str
  conditions:
    description:
    - dictionary defining which conditions to alert on
    - only used for metrics threshold alerts.
    - see examples for details
    type: list
    elements: dict
    suboptions:
      when:
        description:
        - When to trigger the alert
        type: str
        required: true
        choices:
        - max
        - min
        - avg
        - cardnality
        - rate
        - count
        - sum
        - 95th_percentile
        - 99th_percentile
      field:
        description:
        - field of the condition to check
        type: str
      state:
        description:
        - State of the condition
        type: str
        required: true
      threshold:
        description:
        - Alert threshold of the condition
        type: float
        required: true
      warning_threshold:
        description:
        - Warning threshold of the condition
        type: float
      time_period:
        description:
        - Time period
        type: int
        default: 5
      time_unit:
        description:
        - Time unit
        type: str
        default: minute
        choices:
        - second
        - seconds
        - minute
        - minutes
        - hour
        - hours
        - day
        - days
  filter:
    description:
    - kql filter to apply to the conditions
    type: str
  filter_query:
    description:
    - lucence query to apply to the conditions
    - at this time both this and "filter" are required for proper functioning of the
      module
    - easiest way to get this is to do a kibana_alert_facts on an existing alert with
      the correct config
    - alternatively can view the request in the discover tab of kibana
    type: str
  alert_on_no_data:
    description:
    - whether to alert if there is no data available in the check period
    type: bool
    default: false
  group_by:
    description:
    - defines the "alert for every" field in the Kibana alert
    - generally the sensible default is host.name
    type: list
    elements: str
  actions:
    description:
    - actions to run when alert conditions are triggered
    type: list
    elements: dict
    suboptions:
      action_type:
        description:
        - Action type for the alert
        type: str
        required: true
        choices:
        - email
        - index
        - webhook
      run_when:
        description:
        - Run when condition
        type: str
        default: alert
        choices:
        - alert
        - warning
        - recovered
      connector:
        description:
        - Connector for action
        type: str
        required: true
      body:
        description:
        - Action body
        type: str
      body_json:
        description:
        - Action body in json format
        type: dict
  consumer:
    description:
    - name of the application that owns the alert
    default: alerts
    type: str
extends_documentation_fragment:
- expedient.elastic.kibana.documentation
"""

EXAMPLES = """
- name: High CPU Usage
  expedient.elastic.kibana_alert:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    alert_name: High-CPU-Usage
    alert_type: metrics_threshold
    check_every: 5m
    notify_on: status_change
    alert_on_no_data: yes
    group_by: host.name
    conditions:
    - when: avg
      field: system.cpu.total.norm.pct
      state: above
      threshold: .95
      warning_threshold: .85
      time_period: 5
      time_unit: minute
    actions:
    - action_type: webhook
      connector: SMC Alert
      run_when: alert
      body_json:
        hostname: '{{ example }}'
        alert_type: high_cpu
        alert_name: '{{ alertName }}'
        ticket_problem: -1
        alert_status: firing
        group: '{{ group }}'
        alertState: '{{ alertState }}'
        reason: '{{ reason }}'
- name: Disk space alert
  expedient.elastic.kibana_alert:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    alert_name: Disk space alert
    alert_type: metrics_threshold
    check_every: 10m
    notify_on: status_change
    alert_on_no_data: no
    group_by:
    - host.name
    - system.filesystem.mount_point
    conditions:
    - when: max
      field: system.filesystem.used.pct
      state: above
      threshold: .95
      warning_threshold: .85
      time_period: 15
      time_unit: minute
      filter: 'not system.filesystem.type: cdfs'
      filter_query: '{"bool":{"must_not":{"bool":{"should":[{"match":{"system.filesystem.type":"cdfs"}}],"minimum_should_match":1}}}}'
    actions:
    - action_type: webhook
      connector: SMC Alert
      run_when: alert
      body_json:
        hostname: '{{ example }}'
        alert_type: disk_space
        alert_name: '{{ alertName }}'
        ticket_problem: -1
        alert_status: firing
        group: '{{ group }}'
        alertState: '{{ alertState }}'
        reason: '{{ reason }}'
- name: High Memory Usage
  expedient.elastic.kibana_alert:
    host: '{{ kibana_endpoint }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    alert_name: High Memory Usage
    alert_type: metrics_threshold
    check_every: 5m
    notify_on: status_change
    alert_on_no_data: no
    group_by: host.name
    conditions:
    - when: max
      field: system.memory.actual.used.pct
      state: above
      threshold: .90
      warning_threshold: .85
      time_period: 5
      time_unit: minute
    actions:
    - action_type: webhook
      connector: SMC Alert
      run_when: alert
      body_json:
        hostname: '{{ example }}'
        alert_type: high_mem
        alert_name: '{{ alertName }}'
        ticket_problem: -1
        alert_status: firing
        group: '{{ group }}'
        alertState: '{{ alertState }}'
        reason: '{{ reason }}'
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: alert named High-CPU-Usage created
alert:
    description: Alert Information
    returned: changed
    type: dict
    sample: {
            "id": "ec708140-546c-11ec-ae4b-e36fbef57520",
            "notifyWhen": "onActionGroupChange",
            "consumer": "alerts",
            "alertTypeId": "metrics.alert.threshold",
            "schedule": {
                "interval": "5m"
            },
            "actions": [
                {
                    "actionTypeId": ".webhook",
                    "group": "metrics.threshold.fired",
                    "params": {
                        "body": "omitted in example"
                    },
                    "id": "e6010370-546c-11ec-ae4b-e36fbef57520"
                }
            ],
            "tags": [],
            "name": "High-CPU-Usage",
            "enabled": true,
            "throttle": null,
            "apiKeyOwner": "expedient",
            "createdBy": "expedient",
            "updatedBy": "expedient",
            "muteAll": false,
            "mutedInstanceIds": [],
            "params": {
                "criteria": [
                    {
                        "aggType": "avg",
                        "comparator": ">",
                        "threshold": [
                            0.95
                        ],
                        "timeSize": 5,
                        "timeUnit": "m",
                        "metric": "system.cpu.total.norm.pct"
                    }
                ],
                "alertOnNoData": true,
                "sourceId": "default",
                "groupBy": [
                    "host.name"
                ]
            },
            "updatedAt": "2021-12-03T19:12:15.434Z",
            "createdAt": "2021-12-03T19:12:15.434Z",
            "scheduledTaskId": "edddcce0-546c-11ec-ae4b-e36fbef57520",
            "executionStatus": {
                "lastExecutionDate": "2021-12-03T19:12:15.434Z",
                "status": "pending"
            }
        }
"""

from json import dumps
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


time_unit_lookup = {
    "second": "s",
    "seconds": "s",
    "minute": "m",
    "minutes": "m",
    "hour": "h",
    "hours": "h",
    "day": "d",
    "days": "d",
}

alert_type_lookup = {"metrics_threshold": "metrics.alert.threshold"}

action_type_lookup = {"email": ".email", "index": ".index", "webhook": ".webhook"}

# Need to get warning thresholds added here too
action_group_lookup = {
    "alert": "metrics.threshold.fired",
    "recovered": "metrics.threshold.recovered",
}

action_param_type_lookup = {"index": "documents", "webhook": "body"}

state_lookup = {"above": ">", "below": "<"}

notify_lookup = {"status_change": "onActionGroupChange"}


class KibanaAlert(Kibana):
    def __init__(self, module):
        super().__init__(module)
        self.module = module
        self.alert_name = self.module.params.get("alert_name")
        self.alert_type = self.module.params.get("alert_type")
        self.enabled = self.module.params.get("enabled")
        self.tags = self.module.params.get("tags")
        # split the 'check_every' parameter into pieces as needed by elastic API
        self.check_every = self.module.params.get("check_every")
        self.notify_when = self.module.params.get("notify_on")
        self.group_by = self.module.params.get("group_by")
        self.alert_on_no_data = self.module.params.get("alert_on_no_data")
        self.consumer = self.module.params.get("consumer")
        self.filter = self.module.params.get("filter")
        self.filter_query = self.module.params.get("filter_query")

        self.alert = self.get_alert_by_name(self.alert_name)

    def split_time_string(self, time_string):
        tail = time_string.lstrip("0123456789")
        head = time_string[: len(time_string) - len(tail)]
        return head, tail

    # This will defnitely need changes as we expand out functionality of the alert module, currently really only works with metrcis thresholds
    def format_conditions(self):
        conditions = self.module.params.get("conditions")
        formatted_conditions = []
        if self.alert_type == "metrics_threshold":
            for condition in conditions:
                formatted_condition = {
                    "aggType": condition["when"],
                    "comparator": state_lookup[condition["state"]],
                    "threshold": [condition["threshold"]] if condition["threshold"] != 0.0 else [int(condition["threshold"])],
                    "timeSize": condition["time_period"],
                    "timeUnit": time_unit_lookup[condition["time_unit"]],
                }
                if condition["field"] is not None:
                    formatted_condition["metric"] = condition["field"]
                formatted_conditions.append(formatted_condition)
        return formatted_conditions

    def format_actions(self):
        actions = self.module.params.get("actions")
        formatted_actions = [
            {
                "actionTypeId": action_type_lookup[action["action_type"]],
                "group": action_group_lookup[action["run_when"]],
                "params": {action_param_type_lookup[action["action_type"]]: [action["body"]] if action["body"] else dumps(action["body_json"], indent=2)},
                "id": self.get_alert_connector_by_name(action["connector"])["id"],  # need to actually implement this
            }
            for action in actions
        ]
        return formatted_actions

    def create_alert(self):
        endpoint = "alerts/alert"
        criteria = self.format_conditions()
        data = {
            "notifyWhen": notify_lookup[self.notify_when],
            "params": {
                "criteria": criteria,
                "alertOnNoData": self.alert_on_no_data,
                "sourceId": "default",  # entirely unclear what this does but it appears to be a static value so hard-coding for now
            },
            "consumer": self.consumer,
            "alertTypeId": alert_type_lookup[self.alert_type],
            "schedule": {"interval": self.check_every},
            "actions": self.format_actions(),
            "tags": self.tags,
            "name": self.alert_name,
            "enabled": self.enabled,
        }
        if self.filter:
            data["params"]["filterQueryText"] = self.filter
            data["params"]["filterQuery"] = self.filter_query
        if self.group_by:
            data["params"]["groupBy"] = self.group_by
        result = self.send_api_request(endpoint, "POST", data=data)
        return result

    def delete_alert(self):
        endpoint = f'alerts/alert/{self.alert["id"]}'
        return self.send_api_request(endpoint, "DELETE")


def main():
    module_args = kibana_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            alert_name=dict(type="str", required=True),
            enabled=dict(type="bool", default=True),
            alert_type=dict(type="str", choices=["metrics_threshold"]),
            tags=dict(type="list", elements="str"),
            check_every=dict(type="str", default="1m"),
            notify_on=dict(type="str", default="status_change", choices=["status_change"]),
            conditions=dict(
                type="list",
                elements="dict",
                options=dict(
                    when=dict(
                        type="str",
                        required=True,
                        choices=[
                            "max",
                            "min",
                            "avg",
                            "cardnality",
                            "rate",
                            "count",
                            "sum",
                            "95th_percentile",
                            "99th_percentile",
                        ],
                    ),
                    field=dict(type="str", required=False),
                    state=dict(type="str", required=True),
                    threshold=dict(type="float", required=True),
                    warning_threshold=dict(type="float", required=False),  # placeholder not currently implemented
                    time_period=dict(type="int", default=5),
                    time_unit=dict(
                        type="str",
                        default="minute",
                        choices=[
                            "second",
                            "seconds",
                            "minute",
                            "minutes",
                            "hour",
                            "hours",
                            "day",
                            "days",
                        ],
                    ),
                ),
            ),
            filter=dict(type="str"),
            filter_query=dict(type="str"),
            alert_on_no_data=dict(type="bool", default=False),
            group_by=dict(type="list", elements="str"),
            actions=dict(
                type="list",
                elements="dict",
                options=dict(
                    action_type=dict(type="str", required=True, choices=["email", "index", "webhook"]),
                    run_when=dict(
                        type="str",
                        default="alert",
                        choices=["alert", "warning", "recovered"],
                    ),
                    connector=dict(type="str", required=True),
                    body=dict(type="str", required=False),
                    body_json=dict(type="dict", required=False),
                ),
            ),
            consumer=dict(type="str", default="alerts"),
        )
    )

    argument_dependencies = [
        ["state", "present", ["enabled", "alert_type", "conditions", "actions"]],
        ["alert_type", "metrics_threshold", ["conditions"], True],
    ]

    results = {"changed": False}

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=argument_dependencies,
        supports_check_mode=True,
    )
    state = module.params.get("state")
    kibana_alert = KibanaAlert(module)
    if state == "present":
        if kibana_alert.alert:
            results["msg"] = f"alert named {kibana_alert.alert_name} exists"
            module.exit_json(**results)
        results["changed"] = True
        results["msg"] = f'alert named {module.params.get("alert_name")} will be created'
        if not module.check_mode:
            results["alert"] = kibana_alert.create_alert()
            results["msg"] = f'alert named {module.params.get("alert_name")} created'
        module.exit_json(**results)
    if state == "absent":
        if not kibana_alert.alert:
            results["msg"] = f"alert named {kibana_alert.alert_name} does not exist"
            module.exit_json(**results)
        results["changed"] = True
        results["msg"] = f'alert named {module.params.get("alert_name")} will be deleted'
        if not module.check_mode:
            kibana_alert.delete_alert()
        module.exit_json(**results)


if __name__ == "__main__":
    main()
