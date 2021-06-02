# -*- coding: utf-8 -*-

# Options when connecting to ECE

class ModuleDocFragment(object):
  DOCUMENTATION = r'''
options:
  host:
    description:
    - DNS name of the ECE cluster's admin console
    type: str
    required: True
  port:
    description:
    - Port number of ECE cluster admin console
    default: 12443
    type: int
  username:
    description:
    - Username to use when connecting to ECE
    required: True
    type: str
  password:
    description:
    - Password to use when connecting to ECE
    required: True
    type: str
  verify_ssl_cert:
    description:
    - Set whether to verify the SSL cert of the ECE cluster when connecting
    - Should always be True in prod
    default: True
    type: bool

'''