try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

from ansible.module_utils.basic import AnsibleModule

time_unit_lookup = {
  'second': 's',
  'seconds': 's',
  'minute': 'm',
  'minutes': 'm',
  'hour': 'h',
  'hours': 'h',
  'day': 'd',
  'days': 'd',
}

alert_type_lookup = {
  'metrics_threshold': 'metrics.alert.threshold'
}

action_type_lookup = {
  'email': '.email',
  'index': '.index',
  'webhook': '.webhook'
}

# Need to get warning thresholds added here too
action_group_lookup = {
  'alert': 'metrics.threshold.fired',
  'recovered': 'metrics.threshold.recovered'
}

action_param_type_lookup = {
  'index': 'documents',
  'webhook': 'body'
}

state_lookup = {
  'above': '>',
  'below': '<'
}

notify_lookup = {
  'status_change': 'onActionGroupChange'
}
class KibanaAlert(Kibana):
  def __init__(self, module):
    super().__init__(module)
    self.module = module
    self.alert_name = self.module.params.get('alert_name')
    self.alert_type = self.module.params.get('alert_type')
    self.enabled = self.module.params.get('enabled')
    self.tags = self.module.params.get('tags')
    ## split the 'check_every' parameter into pieces as needed by elastic API
    self.check_every = self.module.params.get('check_every')
    self.notify_when = self.module.params.get('notify_on')
    self.group_by = self.module.params.get('group_by')
    self.alert_on_no_data = self.module.params.get('alert_on_no_data')
    self.consumer = self.module.params.get('consumer')



    self.alert = self.get_alert_by_name(self.alert_name)

  def split_time_string(self, time_string):
    tail = time_string.lstrip('0123456789')
    head = time_string[:len(time_string) - len(tail)]
    return head, tail

  # This will defnitely need changes as we expand out functionality of the alert module, currently really only works with metrcis thresholds
  def format_conditions(self):
    conditions = self.module.params.get('conditions')
    return [{
      'aggType': condition['when'],
      'comparator': state_lookup[condition['state']],
      'threshold': [condition['threshold']],
      'timeSize': condition['time_period'],
      'timeUnit': time_unit_lookup[condition['time_unit']],
      'metric': condition['field'],
    } for condition in conditions]

  def format_actions(self):
    actions = self.module.params.get('actions')
    formatted_actions = [{
      'actionTypeId': action_type_lookup[action['action_type']],
      'group': action_group_lookup[action['run_when']],
      'params': {
        action_param_type_lookup[action['action_type']]:[action['body']]
      },
      'id': self.get_alert_connector_by_name(action['connector'])['id'] ## need to actually implement this
    } for action in actions]
    return formatted_actions

  def create_alert(self):
    endpoint = 'alerts/alert'
    criteria = self.format_conditions()
    data = {
      'notifyWhen': notify_lookup[self.notify_when],
      'params': {
        'criteria': criteria,
        'groupBy': self.group_by,
        'alertOnNoData': self.alert_on_no_data,
        'sourceId': 'default' #entirely unclear what this does but it appears to be a static value so hard-coding for now
      },
      'consumer': self.consumer,
      'alertTypeId': alert_type_lookup[self.alert_type],
      'schedule': {
        'interval': self.check_every
      },
      'actions': self.format_actions(),
      'tags': self.tags,
      'name': self.alert_name,
      'enabled': self.enabled
    }
    result = self.send_api_request(endpoint, 'POST', data=data)
    return result






def main():
  module_args=dict(
    host=dict(type='str', required=True),
    port=dict(type='int', default=9243),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify_ssl_cert=dict(type='bool', default=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
    alert_name=dict(type='str', required=True),
    enabled=dict(type='bool', default=True),
    alert_type=dict(type='str', required=True, choices=['metrics_threshold']), #more types will be added as we gain the ability to support them
    tags=dict(type='list', elements='str', default=[]),
    check_every=dict(type='str', default='1m'),
    notify_on=dict(type='str', default='status_change'),
    conditions=dict(type='list', elements='dict', options=dict(
      when=dict(type='str', required=True, choices=['max', 'min', 'average', 'cardnality', 'rate', 'document_count', 'sum', '95th_percentile', '99th_percentile']),
      #comparator=dict(type='str', required=True, choices=['>', '<', '=']),
      field=dict(type='str', required=True),
      state=dict(type='str', required=True),
      threshold=dict(type='float', required=True),
      warning_threshold=dict(type='float', required=False), # placeholder not currently implemented
      time_period=dict(type='int', default=5),
      time_unit=dict(type='str', default='minute', choices=['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']),
    )),
    filter=dict(type='str', required=False),
    alert_on_no_data=dict(type='bool', default=False),
    group_by=dict(type='list', elements='str', default=['host.name']),
    actions=dict(type='list', elements='dict', options=dict(
      action_type=dict(type='str', required=True, choices=['email', 'index', 'webhook']), #Only supporting these types for now, if we need more options later we can deal with them as-needed
      run_when=dict(type='str', default='alert', choices=['alert', 'warning', 'recovered']),
      connector=dict(type='str', required=True),
      body=dict(type='str', required=True)
    )),
    consumer=dict(type='str', default='alerts'), ## This seems to always be the default value at this time, just future-proofing
  )

  results = {'changed': False}

  module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
  state = module.params.get('state')
  kibana_alert = KibanaAlert(module)
  if state == 'present':
    if kibana_alert.alert:
      results['msg'] = f'alert named {kibana_alert.alert_name} exists'
      module.exit_json(**results)
    results['alert'] = kibana_alert.create_alert()
    results['changed'] = True
    module.exit_json(**results)


if __name__ == '__main__':
  main()