try:
  from ansible_collections.expedient.elastic.plugins.module_utils.endgame import Endgame
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from endgame import Endgame

from ansible.module_utils.basic import AnsibleModule


class endgame_saml(Endgame):
  def __init__(self, module):
    super().__init__(module)


def main():
  module_args=dict(
    host=dict(type='str', required=True),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='enabled', choices=['enabled', 'disabled']),
    idp_metadata=dict(type='str', required=True),
    allow_local_login=dict(type='bool', default=True),
    group_mapping=dict(type='dict', default={})
  )