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
  'elastic_query': '.es-query',
  'metrics_threshold': 'metrics.alert.threshold',
  'uptime_monitor_status': 'xpack.uptime.alerts.monitorStatus'
}

action_type_lookup = {
  'email': '.email',
  'index': '.index',
  'webhook': '.webhook'
}

# Need to get warning thresholds added here too
action_group_lookup = {
  'query_matched': 'query matched',
  'alert': 'metrics.threshold.fired',
  'recovered': 'metrics.threshold.recovered',
  'uptime_down_monitor': "xpack.uptime.alerts.actionGroups.monitorStatus"
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
  'status_change': 'onActionGroupChange',
  'active_alert': 'onActiveAlert'
}