## at the moment this is incredibly limited and exists purely to allow for usage reporting

ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}

## need to support both loading as part of a collection and running in test/debug mode
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ansible.module_utils.basic import AnsibleModule


class ECE_Facts(ECE):
  def __init__(self, module):
    super().__init__(module)




module_args = dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=12443),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
  )





results = {'changed': False}
module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
ece_facts = ECE_Facts(module)

results['cluters'] = ece_facts.get_clusters()


if __name__ == '__main__':
  main()