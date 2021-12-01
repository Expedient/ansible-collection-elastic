##################################################################
#
#   Script to create Elastic Integrations
#
#   Version 1.0 - 11/30/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule
#from ansible.module_utils.basic import *

import json
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.ece import ECE
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from ece import ECE
  
try:
  from ansible_collections.expedient.elastic.plugins.module_utils.elastic import Elastic
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from elastic import Elastic

try:
  from ansible_collections.expedient.elastic.plugins.module_utils.kibana import Kibana
except:
  import sys
  import os
  util_path = new_path = f'{os.getcwd()}/plugins/module_utils'
  sys.path.append(util_path)
  from kibana import Kibana

results = {}

class Integration(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module
    
    def get_integrations(self):
        endpoint  = 'fleet/epm/packages'
        integration_objects = self.send_api_request(endpoint, 'GET')
        return integration_objects
    
    def install_integration(self, name, version):
        body = {
            "force": True
        }
        body_JSON = json.dumps(body)
        endpoint  = 'fleet/epm/packages/' + name + "-" + version
        integration_install = self.send_api_request(endpoint, 'POST', data=body_JSON)
        return integration_install
    
    def check_integration(self, integration_name, check_mode=False):
        results['check_mode'] = str(check_mode)
        integration_objects = Integration.get_integrations(self)
        integration_object = ""
        for integration in integration_objects['response']:
          if integration['title'] in integration_name:
            integration_object = integration
            if integration['status'] != 'installed':
              integration_install = Integration.install_integration(self,integration['name'],integration['version'])
        return(integration_object)