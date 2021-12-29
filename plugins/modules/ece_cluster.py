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
module: ece_cluster
short_description: Create modify or delete Elasticsearch clusters in ECE
author: Mike Garuccio (@mgaruccio)
requirements:
- python3
- pyyaml
description:
- This module creates new Elasticsearch clusters in ECE
- supports elasticsearch, Kibana, APM, and ML clusters
version_added: 1.0.0
options:
  state:
    description:
    - The desired state for the module
    choices: [present, absent]
    default: present
    type: str
  cluster_name:
    description:
    - Name for the cluster to create or modify
    required: true
    type: str
  elastic_settings:
    description:
    - Settings for Elastic clusters to create
    type: list
    elements: dict
    suboptions:
      memory_mb:
        description:
        - Amount of memory to assign cluster, in mb
        required: true
        type: int
      instance_config:
        description:
        - Name of the instance configuration to use for the elastic nodes
        type: str
        default: data.logging
      zone_count:
        description:
        - Number of zones to deploy the elasticsearch cluster into
        type: int
        choices: [1, 2, 3]
        default: 2
      roles:
        description:
        - Roles the nodes should fufill
        type: list
        required: true
        choices: [master, data, ingest]
        elements: str
  version:
    description:
    - Version of the Elastic Stack to deploy
    default: 7.13.0
    type: str
  deployment_template:
    description:
    - Name of the deployment template to use when deploying the cluster
    required: true
    type: str
  elastic_user_settings:
    description:
    - Settings object to pass as overrides for the elasticsearch.yml file for the
      cluster
    - Supports all settings definable in elasticsearch.yml
    required: false
    type: dict
  snapshot_settings:
    description:
    - Defines which snapshot repository to use and the retention settings for snapshots
    type: dict
    suboptions:
      repository_name:
        description:
        - Name of the snapshot repository to use for cluster backups
        type: str
        required: true
      snapshots_to_retain:
        description:
        - number of snapshots to retain
        type: int
        default: 100
      snapshot_interval:
        description:
        - How long to wait between snapshots
        - Defined as '60m' for 60 minutes, or '5h' for 5 hours, etc
        type: str
        default: 60m
      enabled:
        description:
        - Whether or not to enable the snapshot repo
        type: bool
        default: true
  kibana_settings:
    description:
    - Settings to apply to the Kibana instances deployed for the elastic cluster
    type: dict
    suboptions:
      memory_mb:
        description:
        - Amount of memory to assign to each Kibana instance, in mb
        required: true
        type: int
      instance_config:
        description:
        - instance configuration to use when creating the Kibana instances
        default: kibana
        type: str
      zone_count:
        description:
        - number of zones to deploy Kibana into
        default: 1
        type: int
  apm_settings:
    description:
    - Settings to apply to the Kibana instances deployed for the elastic cluster
    type: dict
    suboptions:
      memory_mb:
        description:
        - Amount of memory to assign to each APM instance, in mb
        required: true
        type: int
      instance_config:
        description:
        - instance configuration to use when creating the APM instances
        default: apm
        type: str
      zone_count:
        description:
        - number of zones to deploy Kibana into
        default: 1
        type: int
  ml_settings:
    description:
    - Settings to apply to the Kibana instances deployed for the elastic cluster
    type: dict
    suboptions:
      memory_mb:
        description:
        - Amount of memory to assign to each ML instance, in mb
        required: true
        type: int
      instance_config:
        description:
        - instance configuration to use when creating the ML instances
        default: ml
        type: str
      zone_count:
        description:
        - number of zones to deploy Kibana into
        default: 1
        type: int
  wait_for_completion:
    description:
    - Whether to wait for the completion of the cluster operations before exiting
      the module
    - Impacts how much information is returned at the end of the module run
    default: false
    type: bool
  completion_timeout:
    description:
    - How long to wait, in seconds, for operations to complete before timing out
    - only applies if wait_for_completion is True
    default: 600
    type: int
  traffic_rulesets:
    description:
    - Traffic Rulesets
    type: list
    elements: str
extends_documentation_fragment:
- expedient.elastic.ece.documentation
"""

EXAMPLES = """
- name: Get Elastic Info for Test Deployment
  expedient.elastic.ece_cluster_info:
    host: '{{ ece_host }}'
    username: '{{ elastic_username }}'
    password: '{{ elastic_password }}'
    state: present
    deployment_name: test
    cluster_name: Test Deployment
    elastic_settings:
      memory_mb: '{{ elastic_mb }}'
      instance_config: '{{ instance_config }}'
      zone_count: 1
      roles: master
    version: '{{ version }}'
    deployment_template: Test Template
    snapshot_settings:
      repository_name: Testing
    kibana_settings:
      memory_mb: '{{ kibana_mb }}'
    apm_settings:
      memory_mb: '{{ apm_mb }}'
  delegate_to: localhost
"""

RETURN = """
msg:
    description: Summary of changes made
    returned: always
    type: str
    sample: cluster testing created
cluster_data:
    description: Cluster Information
    returned: changed
    type: dict
    contains:
        elasticsearch_cluster_id:
            description: Elastic Search Cluster ID
            returned: changed
            type: str
            sample: 87aa5g3da675454888d4561231b13a0c
        kibana_cluster_id:
            description: Kibana Cluster ID
            returned: changed
            type: str
            sample: fe022ffa175249f1a6d4069ce66fd132
        apm_id:
            description: APM ID
            returned: changed
            type: str
            sample: 1883fb8f126e4a2ah313030a4b3620be
        cloud_id:
            description: Cloud ID
            returned: changed
            type: str
            sample: testing:DFqsd5TrimmedForExamplezDOzGg==
        credentials:
            description: Credentials
            returned: changed
            type: dict
            contains:
                username:
                    description: Username
                    returned: changed
                    type: str
                    sample: elastic
                password:
                    description: Password
                    returned: changed
                    type: str
                    sample: password_omitted
        apm:
            description: APM Information
            returned: changed
            type: dict
            contains:
                apm_id:
                    description: APM ID
                    returned: changed
                    type: str
                    sample: 1883fb8f126e4a2ah313030a4b3620be
                secret_token:
                    description: Secret Token for APM
                    returned: changed
                    type: str
                    sample: secret_omitted
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback

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

try:
    from yaml import dump

    try:
        from yaml import CDumper as Dumper
    except ImportError:
        from yaml import Dumper
except ImportError:
    HAS_YAML = False
    YAML_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_YAML = True


class ECE_Cluster(ECE):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_name = self.module.params.get("cluster_name")
        self.elastic_settings = self.module.params.get("elastic_settings")
        self.kibana_settings = self.module.params.get("kibana_settings")
        self.apm_settings = self.module.params.get("apm_settings")
        self.ml_settings = self.module.params.get("ml_settings")
        self.version = self.module.params.get("version")
        self.deployment_template = self.module.params.get("deployment_template")
        self.wait_for_completion = self.module.params.get("wait_for_completion")
        self.completion_timeout = self.module.params.get("completion_timeout")
        self.elastic_user_settings = self.module.params.get("elastic_user_settings")
        self.snapshot_settings = self.module.params.get("snapshot_settings")
        self.traffic_rulesets = self.module.params.get("traffic_rulesets")

    def get_matching_clusters(self):
        clusters = self.get_clusters_by_name(self.cluster_name)
        return clusters

    def create_cluster(self):
        data = {
            "cluster_name": self.cluster_name,
            "plan": {
                "cluster_topology": [
                    {
                        "size": {"value": settings["memory_mb"], "resource": "memory"},
                        "node_type": {
                            "master": "master" in settings["roles"],
                            "data": "data" in settings["roles"],
                            "ingest": "ingest" in settings["roles"],
                        },
                        "instance_configuration_id": self.get_instance_config(settings["instance_config"])["id"],
                        "elasticsearch": {
                            "enabled_built_in_plugins": [],
                            "node_attributes": {},
                            "user_settings_yaml": dump(self.elastic_user_settings, Dumper=Dumper),
                        },
                        "zone_count": settings["zone_count"],
                    }
                    for settings in self.elastic_settings
                ],
                "elasticsearch": {"version": self.version},
                "transient": {},
                "deployment_template": {"id": self.get_deployment_template(self.deployment_template)["id"]},
            },
            "settings": {},
            "kibana": {
                "plan": {
                    "cluster_topology": [
                        {
                            "instance_configuration_id": self.get_instance_config(self.kibana_settings["instance_config"])["id"],
                            "size": {
                                "value": self.kibana_settings["memory_mb"],
                                "resource": "memory",
                            },
                            "zone_count": self.kibana_settings["zone_count"],
                        }
                    ],
                    "kibana": {
                        # using a default value here, if we want to extend it later it can be
                        "user_settings_yaml": "# Note that the syntax for user settings can change between major versions.",
                        "version": self.version,
                    },
                },
            },
        }

        if self.apm_settings:
            data["apm"] = {
                "plan": {
                    "cluster_topology": [
                        {
                            "instance_configuration_id": self.get_instance_config(self.apm_settings["instance_config"])["id"],
                            "size": {
                                "value": self.apm_settings["memory_mb"],
                                "resource": "memory",
                            },
                            "zone_count": self.apm_settings["zone_count"],
                        }
                    ],
                    "apm": {"version": self.version},
                }
            }

        # This is technically just another ES deployment rather than it's own config, but decided to follow the UI rather than API conventions
        if self.ml_settings:
            data["plan"]["cluster_topology"].append(
                {
                    "instance_configuration_id": self.get_instance_config(self.ml_settings["instance_config"])["id"],
                    "size": {
                        "value": self.ml_settings["memory_mb"],
                        "resource": "memory",
                    },
                    "node_type": {
                        "master": False,
                        "data": False,
                        "ingest": False,
                        "ml": True,
                    },
                    "zone_count": self.ml_settings["zone_count"],
                }
            )

        if self.snapshot_settings:
            data["settings"]["snapshot"] = {
                "repository": {"reference": {"repository_name": self.snapshot_settings["repository_name"]}},
                "enabled": self.snapshot_settings["enabled"],
                "retention": {
                    "snapshots": self.snapshot_settings["snapshots_to_retain"],
                },
                "interval": self.snapshot_settings["snapshot_interval"],
            }

        if self.traffic_rulesets:
            data["settings"]["ip_filtering"] = {"rulesets": [self.get_traffic_ruleset_by_name(x)["id"] for x in self.traffic_rulesets]}

        endpoint = "clusters/elasticsearch"
        cluster_creation_result = self.send_api_request(endpoint, "POST", data=data)
        if self.wait_for_completion:
            elastic_result = self.wait_for_cluster_state(
                "elasticsearch",
                cluster_creation_result["elasticsearch_cluster_id"],
                "started",
                self.completion_timeout,
            )
            kibana_result = self.wait_for_cluster_state(
                "kibana",
                cluster_creation_result["kibana_cluster_id"],
                "started",
                self.completion_timeout,
            )
            if not elastic_result and kibana_result:
                return False
        return cluster_creation_result

    def delete_cluster(self, cluster_id):
        self.terminate_cluster(cluster_id)
        endpoint = f"clusters/elasticsearch/{cluster_id}"
        delete_result = self.send_api_request(endpoint, "DELETE")
        return delete_result

    def terminate_cluster(self, cluster_id):
        endpoint = f"clusters/elasticsearch/{cluster_id}/_shutdown"
        stop_result = self.send_api_request(endpoint, "POST")
        wait_result = self.wait_for_cluster_state("elasticsearch", cluster_id, "stopped", self.completion_timeout)
        if not wait_result:
            self.module.fail_json(msg=f"failed to stop cluster {self.cluster_name}")
        return stop_result


def main():
    elastic_settings_spec = dict(
        memory_mb=dict(type="int", required=True),
        instance_config=dict(type="str", default="data.logging"),
        zone_count=dict(type="int", default=2, choices=[1, 2, 3]),
        roles=dict(type="list", required=True, elements="str", choices=["master", "data", "ingest"]),
    )
    snapshot_settings_spec = dict(
        repository_name=dict(type="str", required=True),
        snapshots_to_retain=dict(type="int", default=100),
        snapshot_interval=dict(type="str", default="60m"),
        enabled=dict(type="bool", default=True),
    )
    kibana_settings_spec = dict(
        memory_mb=dict(type="int", required=True),
        instance_config=dict(type="str", default="kibana"),
        zone_count=dict(type="int", default=1),
    )
    apm_settings_spec = dict(
        memory_mb=dict(type="int", required=True),
        instance_config=dict(type="str", default="apm"),
        zone_count=dict(type="int", default=1),
    )
    ml_settings_spec = dict(
        memory_mb=dict(type="int", required=True),
        instance_config=dict(type="str", default="ml"),
        zone_count=dict(type="int", default=1),
    )

    module_args = ece_argument_spec()
    module_args.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            cluster_name=dict(type="str", required=True),
            elastic_settings=dict(type="list", elements="dict", options=elastic_settings_spec),
            elastic_user_settings=dict(type="dict", default={}),  # does not have sub-options defined as there are far too many elastic options to capture here
            snapshot_settings=dict(type="dict", options=snapshot_settings_spec),
            traffic_rulesets=dict(type="list", elements="str"),
            kibana_settings=dict(type="dict", options=kibana_settings_spec),
            apm_settings=dict(type="dict", options=apm_settings_spec),
            ml_settings=dict(type="dict", options=ml_settings_spec),
            version=dict(type="str", default="7.13.0"),
            deployment_template=dict(type="str", required=True),
            wait_for_completion=dict(type="bool", default=False),
            completion_timeout=dict(type="int", default=600),
        )
    )

    results = {"changed": False}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_YAML:
        module.fail_json(msg=missing_required_lib("pyyaml"), exception=YAML_IMPORT_ERROR)

    state = module.params.get("state")
    ece_cluster = ECE_Cluster(module)

    matching_clusters = ece_cluster.get_matching_clusters()
    if len(matching_clusters) > 1:
        results["msg"] = f'found multiple clusters matching name {module.params.get("cluster_name")}'
        module.fail_json(**results)

    if state == "present":
        if len(matching_clusters) > 0:
            results["msg"] = "cluster exists"
            # This code handles edge cases poorly, in the interest of being able to match the data format of the cluster creation result
            results["cluster_data"] = {
                "elasticsearch_cluster_id": matching_clusters[0]["cluster_id"],
                "kibana_cluster_id": matching_clusters[0]["associated_kibana_clusters"][0]["kibana_id"],
            }
            if len(matching_clusters[0]["associated_apm_clusters"]) > 0:
                results["cluster_data"]["apm_id"] = matching_clusters[0]["associated_apm_clusters"][0]["apm_id"]
            module.exit_json(**results)

        results["changed"] = True
        results["msg"] = f'cluster {module.params.get("cluster_name")} will be created'
        if not module.check_mode:
            cluster_data = ece_cluster.create_cluster()
            if not cluster_data:
                results["msg"] = "cluster creation failed"
                module.fail_json(**results)
            results["cluster_data"] = cluster_data
            results["msg"] = f'cluster {module.params.get("cluster_name")} created'
        module.exit_json(**results)

    if state == "absent":
        if len(matching_clusters) == 0:
            results["msg"] = f'cluster {module.params.get("cluster_name")} does not exist'
            module.exit_json(**results)

        results["msg"] = f'cluster {module.params.get("cluster_name")} will be deleted'
        if not module.check_mode:
            results["changed"] = True
            ece_cluster.delete_cluster(matching_clusters[0]["cluster_id"])
            results["msg"] = f'cluster {module.params.get("cluster_name")} deleted'
            module.exit_json(**results)


if __name__ == "__main__":
    main()
