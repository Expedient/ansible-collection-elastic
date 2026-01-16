try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

from ansible.module_utils.basic import AnsibleModule

def main():
  module_args=dict(
    host=dict(type='str'),
    port=dict(type='int'),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    deployment_info=dict(type='dict', default=None),
    policy_id=dict(type='str', required=True)
  )



  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args)
  kibana = Kibana(module)
  policy_id = module.params.get('policy_id')

  enrollment_tokens = kibana.get_agentpolicy_enrollment_tokens()
  import pprint
  pprint.pprint(enrollment_tokens)
  for token in enrollment_tokens['items']:
    if token['policy_id'] == policy_id:
      enrollment_token = token['api_key']
      break
  results['enrollment_token'] = enrollment_token
  module.exit_json(**results)

if __name__ == '__main__':
  main()