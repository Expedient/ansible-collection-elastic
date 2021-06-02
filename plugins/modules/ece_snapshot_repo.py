ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: ece_snapshot_repo

short_description: Create or delete a snapshot repository

version_added: '2.9'

author: Mike Garuccio (@mgaruccio)

requirements:
  - python3

description:
  - "This module creates or deletes a snapshot repo in ECE"
  - "S3 bucket must be created before attempting to use a repo"

options:
  state:
    description:
      - The desired state for the snapshot repo
    choices:
      - present
      - absent
    default: presnet
    type: str
  name:
    description:
      - name of the snapshot repo
    type: str
    required: true
  endpoint:
    description:
      - S3 endpoint to connect to
    type: str
    default: s3.amazonaws.com
  region:
    description:
      - S3 region to connect to
    type: str
    default: us-east-1
  bucket:
    description:
      - S3 bucket to use for snapshot data
    type: str
    required: True
  access_key:
    description:
      - Access key for the S3 bucket
    type: str
    required: True
  secret_key:
    description:
      - secret key for the S3 bucket
    type: str
    required: True

extends_documentation_fragment:
  - expedient.elastic.ece_auth_options
'''

try:
  from ansible_collections.expedient.elastic.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

from ansible.module_utils.basic import AnsibleModule


class ECE_snapshot_repo(ECE):
  def __init__(self, module):
    super().__init__(module)
    self.name = self.module.params.get('name')
    self.repo_type = self.module.params.get('repo_type')
    self.region = self.module.params.get('region')
    self.endpoint = self.module.params.get('endpoint')
    self.bucket = self.module.params.get('bucket')
    self.access_key = self.module.params.get('access_key')
    self.secret_key = self.module.params.get('secret_key')
    self.use_path_style_access = self.module.params.get('use_path_style_access')
    self.protocol = self.module.params.get('protocol')

    self.repo = self.get_snapshot_repo_by_name(self.name)

  def create_snapshot_repo(self):
    endpoint = f'platform/configuration/snapshots/repositories/{self.name}'
    data = {
      'type': self.repo_type,
      'settings': {
        'endpoint': self.endpoint,
        'region': self.region,
        'bucket': self.bucket,
        'secret_key': self.secret_key,
        'access_key': self.access_key,
        'path_style_access': self.use_path_style_access,
        "protocol": self.protocol
      }
    }
    creation_result = self.send_api_request(endpoint, 'PUT', data=data)
    return creation_result

  def delete_snapshot_repo(self):
    endpoint = f'platform/configuration/snapshots/repositories/{self.name}'
    result = self.send_api_request(endpoint, 'DELETE')
    return result




def main():
  module_args = dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present'),
    name=dict(type='str', required=True),
    repo_type=dict(type='str', default='S3'),
    endpoint=dict(type='str', default='s3.amazonaws.com'),
    region=dict(type='str', default='us-east-1'),
    bucket=dict(type='str', required=True),
    access_key=dict(type='str', required=True),
    secret_key=dict(type='str', required=True, no_log=True),
    use_path_style_access=dict(type=bool, default=True),
    protocol=dict(type='str', default='https')
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
  state = module.params.get('state')
  snapshot_repo = ECE_snapshot_repo(module)

  if state == 'present':
    if snapshot_repo.repo:
      results['msg'] = f'repo {snapshot_repo.name} exists'
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'creating snapshot repository {module.params.get("name")}'
    if module.check_mode:
      module.exit_json(**results)
    results['repo'] = snapshot_repo.create_snapshot_repo()
    results['msg'] = f'created snapshot repository {module.params.get("name")}'
    module.exit_json(**results)

  if state == 'absent':
    if not snapshot_repo.repo:
      results['msg'] = f'repo {snapshot_repo.name} does not exist'
      module.exit_json(**results)
    results['changed'] = True
    results['msg'] = f'deleting snapshot repository {module.params.get("name")}'
    if module.check_mode:
      module.exit_json(**results)
    snapshot_repo.delete_snapshot_repo()
    results['msg'] = f'deleted snapshot repository {module.params.get("name")}'
    module.exit_json(**results)






if __name__ == '__main__':
  main()