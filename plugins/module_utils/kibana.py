from ansible.module_utils.urls import open_url, urllib_error
from json import loads, dumps
from urllib.error import HTTPError
import urllib.parse

class Kibana(object):
  def __init__(self, module):
    self.module = module
    self.host = module.params.get('host')
    self.port = module.params.get('port')
    self.username = module.params.get('username')
    self.password = module.params.get('password')
    self.validate_certs = module.params.get('verify_ssl_cert')
    self.version = None # this is a hack to make it so that we can run the first request to get the clutser version without erroring out
    self.version = self.get_cluster_version()

  def send_api_request(self, endpoint, method, data=None):
    url = f'https://{self.host}:{self.port}/api/{endpoint}'
    headers = {}
    payload = None
    if data:
      headers['Content-Type'] = 'application/json'
      payload = dumps(data)
    if self.version:
      headers['kbn-version'] = self.version
    try:
      response = open_url(url, data=payload, method=method, validate_certs=self.validate_certs, headers=headers,
                          force_basic_auth=True, url_username=self.username, url_password=self.password, timeout=60)
    except HTTPError as e:
      raise e ## This allows errors raised during the request to be inspected while debugging
    return loads(response.read())

  def get_cluster_status(self):
    endpoint = 'status'
    return self.send_api_request(endpoint, 'GET')

  def get_cluster_version(self):
    status = self.get_cluster_status()
    return status['version']['number']

  def get_alert_types(self):
    endpoint = 'alert/types'
    alert_types = self.send_api_request(endpoint, 'GET')
    return alert_types

  def get_alert_by_name(self, alert_name):
    endpoint = f'alerts/_find?search_fields=name&search={urllib.parse.quote(alert_name)}'
    alerts = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == alert_name, alerts['data']), None)

  def get_alert_connector_by_name(self, connector_name):
    endpoint = 'actions/connectors'
    actions = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == connector_name, actions), None)

  def get_alert_connector_type_by_name(self, connector_type_name):
    endpoint = 'actions/connector_types'
    connector_types = self.send_api_request(endpoint, 'GET')
    return next(filter(lambda x: x['name'] == connector_type_name, connector_types), None)