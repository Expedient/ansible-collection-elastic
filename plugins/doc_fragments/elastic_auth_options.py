# -*- coding: utf-8 -*-

# Options when connecting to ECE

class ModuleDocFragment(object):
  DOCUMENTATION = r'''
options:
  host:
    description:
    - DNS name of the the Elasticsearch instance
    type: str
    required: True
  port:
    description:
    - Port number of the Elasticsearch instance
    default: 12443
    type: int
  username:
    description:
    - Username to use when connecting to Elasticsearch
    required: True
    type: str
  password:
    description:
    - Password to use when connecting to Elasticsearch
    required: True
    type: str
  verify_ssl_cert:
    description:
    - Set whether to verify the SSL cert of the Elasticsearch cluster when connecting
    - Should always be True in prod
    default: True
    type: bool

'''