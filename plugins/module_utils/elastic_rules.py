##################################################################
#
#   Script to create Elastic Rules in Deployment
#
#   Version 1.0 - 11/30/2021 - Ian Scott - Initial Draft
#
##################################################################

from ansible.module_utils.basic import _ANSIBLE_ARGS, AnsibleModule

import json

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

class Rules(Kibana):
    def __init__(self,module):
        super().__init__(module)
        self.module = module

    def update_rule(self, body):
      endpoint = "detection_engine/rules"
      update_rule = self.send_api_request(endpoint,'PATCH',data=body)
      return update_rule

    def get_rules(self,page_size,page_no):
      endpoint = "detection_engine/rules/_find?page=" + str(page_no) + "&per_page=" + str(page_size)
      rules = self.send_api_request(endpoint, 'GET')
      return rules
    
    def enable_rule(self,rule_id):
      body={
        'enabled': True,
        'id': rule_id
      }
      body_JSON = json.dumps(body)
      update_rule = Rules.update_rule(self, body)
      return update_rule
  
    def activating_all_rules(self, page_size):

      #### Getting first page of rules
      page_number = 1
      rules = Rules.get_rules(self,page_size,page_number)
      noOfRules = rules['total']
      allrules = rules['data']
      #### Going through each rule page by page and enabling each rule that isn't enabled.
      while noOfRules > page_size * (page_number - 1):
          for rule in allrules:
            if rule['enabled'] == False:
              enable_rule = Rules.enable_rule(self,rule['id'])
              return(rule['id'] + ": Rule is updated")
          page_number = page_number + 1
          rules = Rules.get_rules(self,page_size,page_number)
          allrules = rules['data']
      return("Rules are updated")
  