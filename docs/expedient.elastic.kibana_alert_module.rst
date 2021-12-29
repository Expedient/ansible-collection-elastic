.. _expedient.elastic.kibana_alert_module:


******************************
expedient.elastic.kibana_alert
******************************

**Create or delete alerts in Kibana**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module creates or deletes alerts in kibana
- currently supports threshold alerts



Requirements
------------
The below requirements are needed on the host that executes this module.

- python3


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>actions</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>actions to run when alert conditions are triggered</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>action_type</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>email</li>
                                    <li>index</li>
                                    <li>webhook</li>
                        </ul>
                </td>
                <td>
                        <div>Action type for the alert</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>body</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Action body</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>body_json</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Action body in json format</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>connector</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Connector for action</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>run_when</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>alert</b>&nbsp;&larr;</div></li>
                                    <li>warning</li>
                                    <li>recovered</li>
                        </ul>
                </td>
                <td>
                        <div>Run when condition</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>alert_name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>name of the alert to create</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>alert_on_no_data</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>whether to alert if there is no data available in the check period</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>alert_type</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>metrics_threshold</li>
                        </ul>
                </td>
                <td>
                        <div>Alert Type</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>check_every</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"1m"</div>
                </td>
                <td>
                        <div>frequency to check the alert on</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>conditions</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>dictionary defining which conditions to alert on</div>
                        <div>only used for metrics threshold alerts.</div>
                        <div>see examples for details</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>field</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>field of the condition to check</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>State of the condition</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>threshold</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">float</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Alert threshold of the condition</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>time_period</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">5</div>
                </td>
                <td>
                        <div>Time period</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>time_unit</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>second</li>
                                    <li>seconds</li>
                                    <li><div style="color: blue"><b>minute</b>&nbsp;&larr;</div></li>
                                    <li>minutes</li>
                                    <li>hour</li>
                                    <li>hours</li>
                                    <li>day</li>
                                    <li>days</li>
                        </ul>
                </td>
                <td>
                        <div>Time unit</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>warning_threshold</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">float</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Warning threshold of the condition</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>when</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>max</li>
                                    <li>min</li>
                                    <li>avg</li>
                                    <li>cardnality</li>
                                    <li>rate</li>
                                    <li>count</li>
                                    <li>sum</li>
                                    <li>95th_percentile</li>
                                    <li>99th_percentile</li>
                        </ul>
                </td>
                <td>
                        <div>When to trigger the alert</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>consumer</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"alerts"</div>
                </td>
                <td>
                        <div>name of the application that owns the alert</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>enabled</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>whether to enable the alert when creating</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>filter</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>kql filter to apply to the conditions</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>filter_query</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>lucence query to apply to the conditions</div>
                        <div>at this time both this and &quot;filter&quot; are required for proper functioning of the module</div>
                        <div>easiest way to get this is to do a kibana_alert_facts on an existing alert with the correct config</div>
                        <div>alternatively can view the request in the discover tab of kibana</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>group_by</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>defines the &quot;alert for every&quot; field in the Kibana alert</div>
                        <div>generally the sensible default is host.name</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>host</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>DNS name of the the Kibana instance</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>notify_on</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>status_change</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>when to send the alert</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>password</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Password to use when connecting to Kibana</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">9243</div>
                </td>
                <td>
                        <div>Port number of the Kibana instance</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                    <li>absent</li>
                        </ul>
                </td>
                <td>
                        <div>setting whether alert should be created or deleted</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>tags</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>metadata tags to attach to the alert</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>username</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Username to use when connecting to Kibana</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>validate_certs</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Set whether to verify the SSL cert of the Kibana cluster when connecting</div>
                        <div>Should always be True in prod</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: verify_ssl_cert</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: High CPU Usage
      expedient.elastic.kibana_alert:
        host: '{{ kibana_endpoint }}'
        username: '{{ elastic_username }}'
        password: '{{ elastic_password }}'
        state: present
        alert_name: High-CPU-Usage
        alert_type: metrics_threshold
        check_every: 5m
        notify_on: status_change
        alert_on_no_data: yes
        group_by: host.name
        conditions:
        - when: avg
          field: system.cpu.total.norm.pct
          state: above
          threshold: .95
          warning_threshold: .85
          time_period: 5
          time_unit: minute
        actions:
        - action_type: webhook
          connector: SMC Alert
          run_when: alert
          body_json:
            hostname: '{{ example }}'
            alert_type: high_cpu
            alert_name: '{{ alertName }}'
            ticket_problem: -1
            alert_status: firing
            group: '{{ group }}'
            alertState: '{{ alertState }}'
            reason: '{{ reason }}'
    - name: Disk space alert
      expedient.elastic.kibana_alert:
        host: '{{ kibana_endpoint }}'
        username: '{{ elastic_username }}'
        password: '{{ elastic_password }}'
        state: present
        alert_name: Disk space alert
        alert_type: metrics_threshold
        check_every: 10m
        notify_on: status_change
        alert_on_no_data: no
        group_by:
        - host.name
        - system.filesystem.mount_point
        conditions:
        - when: max
          field: system.filesystem.used.pct
          state: above
          threshold: .95
          warning_threshold: .85
          time_period: 15
          time_unit: minute
          filter: 'not system.filesystem.type: cdfs'
          filter_query: '{"bool":{"must_not":{"bool":{"should":[{"match":{"system.filesystem.type":"cdfs"}}],"minimum_should_match":1}}}}'
        actions:
        - action_type: webhook
          connector: SMC Alert
          run_when: alert
          body_json:
            hostname: '{{ example }}'
            alert_type: disk_space
            alert_name: '{{ alertName }}'
            ticket_problem: -1
            alert_status: firing
            group: '{{ group }}'
            alertState: '{{ alertState }}'
            reason: '{{ reason }}'
    - name: High Memory Usage
      expedient.elastic.kibana_alert:
        host: '{{ kibana_endpoint }}'
        username: '{{ elastic_username }}'
        password: '{{ elastic_password }}'
        state: present
        alert_name: High Memory Usage
        alert_type: metrics_threshold
        check_every: 5m
        notify_on: status_change
        alert_on_no_data: no
        group_by: host.name
        conditions:
        - when: max
          field: system.memory.actual.used.pct
          state: above
          threshold: .90
          warning_threshold: .85
          time_period: 5
          time_unit: minute
        actions:
        - action_type: webhook
          connector: SMC Alert
          run_when: alert
          body_json:
            hostname: '{{ example }}'
            alert_type: high_mem
            alert_name: '{{ alertName }}'
            ticket_problem: -1
            alert_status: firing
            group: '{{ group }}'
            alertState: '{{ alertState }}'
            reason: '{{ reason }}'



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>alert</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>changed</td>
                <td>
                            <div>Alert Information</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;id&#x27;: &#x27;ec708140-546c-11ec-ae4b-e36fbef57520&#x27;, &#x27;notifyWhen&#x27;: &#x27;onActionGroupChange&#x27;, &#x27;consumer&#x27;: &#x27;alerts&#x27;, &#x27;alertTypeId&#x27;: &#x27;metrics.alert.threshold&#x27;, &#x27;schedule&#x27;: {&#x27;interval&#x27;: &#x27;5m&#x27;}, &#x27;actions&#x27;: [{&#x27;actionTypeId&#x27;: &#x27;.webhook&#x27;, &#x27;group&#x27;: &#x27;metrics.threshold.fired&#x27;, &#x27;params&#x27;: {&#x27;body&#x27;: &#x27;omitted in example&#x27;}, &#x27;id&#x27;: &#x27;e6010370-546c-11ec-ae4b-e36fbef57520&#x27;}], &#x27;tags&#x27;: [], &#x27;name&#x27;: &#x27;High-CPU-Usage&#x27;, &#x27;enabled&#x27;: True, &#x27;throttle&#x27;: None, &#x27;apiKeyOwner&#x27;: &#x27;expedient&#x27;, &#x27;createdBy&#x27;: &#x27;expedient&#x27;, &#x27;updatedBy&#x27;: &#x27;expedient&#x27;, &#x27;muteAll&#x27;: False, &#x27;mutedInstanceIds&#x27;: [], &#x27;params&#x27;: {&#x27;criteria&#x27;: [{&#x27;aggType&#x27;: &#x27;avg&#x27;, &#x27;comparator&#x27;: &#x27;&gt;&#x27;, &#x27;threshold&#x27;: [0.95], &#x27;timeSize&#x27;: 5, &#x27;timeUnit&#x27;: &#x27;m&#x27;, &#x27;metric&#x27;: &#x27;system.cpu.total.norm.pct&#x27;}], &#x27;alertOnNoData&#x27;: True, &#x27;sourceId&#x27;: &#x27;default&#x27;, &#x27;groupBy&#x27;: [&#x27;host.name&#x27;]}, &#x27;updatedAt&#x27;: &#x27;2021-12-03T19:12:15.434Z&#x27;, &#x27;createdAt&#x27;: &#x27;2021-12-03T19:12:15.434Z&#x27;, &#x27;scheduledTaskId&#x27;: &#x27;edddcce0-546c-11ec-ae4b-e36fbef57520&#x27;, &#x27;executionStatus&#x27;: {&#x27;lastExecutionDate&#x27;: &#x27;2021-12-03T19:12:15.434Z&#x27;, &#x27;status&#x27;: &#x27;pending&#x27;}}</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>msg</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>Summary of changes made</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">alert named High-CPU-Usage created</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Mike Garuccio (@mgaruccio)
