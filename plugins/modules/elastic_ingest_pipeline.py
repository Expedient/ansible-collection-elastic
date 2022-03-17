#!/usr/bin/python
# Copyright 202 Expedient
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

ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: elastic_ingest_pipeline

short_description: ingest pipeline management for elastic

version_added: 2.1.0

author: Mike Garuccio (@mgaruccio)

requirements:
  - python3

description:
  - this module creates or deletes elastc ingest pipelines
  - Update state not yet implemented

options:
  state:
    description:
      - the desired state of the ingest pipeline
    choices:
      - present
      - absent
    default: present
    type: str
  name:
    description:
      - name (id) of the pipeline to create
    type: str
    required: True
  description:
    description:
      - user provided description of the ingest pipeline
    type: str
    required: False
  processors:
    description:
      - list of processors to execute when ingesting data
    type: list
    elements: dict
    required: True
  on_failure:
    description:
      - list of processors to execute if main processors fail
    type: list
    elements: dict
    required: False

extends_documentation_fragment:
  - expedient.elastic.elastic_auth_options
'''


try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

from ansible.module_utils.basic import AnsibleModule


class ElasticIngestPipeline(Elastic):
  def __init__(self, module):
    super().__init__(module)
    self.name = self.module.params.get('name')
    self.description = self.module.params.get('description')
    self.on_failure = self.module.params.get('on_failure')
    self.processors = self.module.params.get('processors')
    self.pipeline = self.get_ingest_pipeline(self.name)

  def create_ingest_pipeline(self):
    endpoint = f'_ingest/pipeline/{self.name}'
    data = {
      'processors': self.processors
    }
    if self.description:
      data['description'] = self.description
    if self.on_failure:
      data['on_failure'] = self.on_failure
    return self.send_api_request(endpoint, data=data, method='PUT')

  def delete_ingest_pipeline(self):
    endpoint = f'_ingest/pipeline/{self.name}'
    return self.send_api_request(endpoint, method='DELETE')




def main():
  module_args=dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=9243),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    name=dict(type='str', required=True),
    description=dict(type='str', required=False),
    on_failure=dict(type='list', elements='dict', required=False),
    processors=dict(type='list', elements='dict', required=True)
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
  state = module.params.get('state')
  elastic_pipeline = ElasticIngestPipeline(module)

  if state == 'present':
    if elastic_pipeline.pipeline:
      results['msg'] = f'pipeline {elastic_pipeline.name} exists'
      results['pipeline'] = elastic_pipeline.pipeline
      module.exit_json(**results)

    results['changed'] = True
    if not module.check_mode:
      results['creation_result'] = elastic_pipeline.create_ingest_pipeline()
      results['pipeline'] = elastic_pipeline.get_ingest_pipeline(elastic_pipeline.name)

  if state == 'absent':
    if not elastic_pipeline.pipeline:
      results['msg'] = f'pipeline {elastic_pipeline.name} does not exist'
      module.exit_json(**results)

    results['changed'] = True
    if not module.check_mode:
      results['deletion_result'] = elastic_pipeline.delete_ingest_pipeline()

  module.exit_json(**results)

if __name__ == '__main__':
  main()

