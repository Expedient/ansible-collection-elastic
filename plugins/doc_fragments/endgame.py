# Copyright 2021 Expedient
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Options when connecting to Endgame


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  host:
    description:
    - DNS name of the the Endgame instance
    type: str
    required: True
  port:
    description:
    - Port number of the Endgame instance
    default: 12443
    type: str
  username:
    description:
    - Username to use when connecting to Endgame
    required: True
    type: str
  password:
    description:
    - Password to use when connecting to Endgame
    required: True
    type: str
  validate_certs:
    description:
    - Set whether to verify the SSL cert of the Endgame cluster when connecting
    - Should always be True in prod
    default: True
    type: bool
    aliases:
    - verify_ssl_cert
'''
