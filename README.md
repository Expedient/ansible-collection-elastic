# Ansible Collection: expedient.elastic

This repo hosts the `expedient.elastic` Ansible Collection.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the Expedient elastic collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install expedient.elastic

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: expedient.elastic
```

### Required Python libraries

Expedient Elastic collection depends upon following third party libraries:

* [`PyYAML`](https://pyyaml.org/wiki/PyYAMLDocumentation)

### Installing required libraries and SDK

Installing collection does not install any required third party Python libraries or SDKs. You need to install the required Python libraries using following command:

    pip install -r ~/.ansible/collections/ansible_collections/expedient/elastic/requirements.txt


## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
[expedient.elastic.ece_cluster](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_cluster_module.rst)|Create modify or delete Elasticsearch clusters in ECE
[expedient.elastic.ece_cluster_info](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_cluster_info_module.rst)|Return ECE cluster information
[expedient.elastic.ece_facts](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_facts_module.rst)|Return ECE cluster information for all clusters
[expedient.elastic.ece_snapshot_repo](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_snapshot_repo_module.rst)|Create or delete a snapshot repository
[expedient.elastic.ece_traffic_ruleset](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_traffic_ruleset_module.rst)|Placeholder
[expedient.elastic.elastic_agentlist_info](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_agentlist_info_module.rst)|Returns Elastic agent list information
[expedient.elastic.elastic_agentpolicy](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_agentpolicy_module.rst)|Configures Elastic agent policy
[expedient.elastic.elastic_agentpolicy_info](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_agentpolicy_info_module.rst)|Returns Elastic agent policy information by id or name
[expedient.elastic.elastic_endpoint_security](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_endpoint_security_module.rst)|Configure Elastic Endpoint Security
[expedient.elastic.elastic_pkgpolicy](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_pkgpolicy_module.rst)|Configure Elastic package policy
[expedient.elastic.elastic_pkgpolicy_info](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_pkgpolicy_info_module.rst)|Returns Elastic package policy information by name
[expedient.elastic.elastic_role_mapping](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_role_mapping_module.rst)|Elastic role mapping
[expedient.elastic.elastic_security_rule](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_security_rule_module.rst)|Elastic security rule
[expedient.elastic.elastic_user](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_user_module.rst)|elastic user management
[expedient.elastic.kibana_action](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.kibana_action_module.rst)|Configure Kibana action
[expedient.elastic.kibana_alert](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.kibana_alert_module.rst)|Create or delete alerts in Kibana
[expedient.elastic.kibana_alert_facts](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.kibana_alert_facts_module.rst)|get info on a kibana alert

<!--end collection content-->

## Contributing to this collection
If you want to develop new content for this collection or improve what is already here, please see the [contributing instructions](CONTRIBUTING.md).
