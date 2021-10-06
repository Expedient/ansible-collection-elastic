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
## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
[expedient.elastic.ece_cluster](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_cluster_module.rst)|Create modify or delete Elasticsearch clusters in ECE
[expedient.elastic.ece_snapshot_repo](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_snapshot_repo_module.rst)|Create or delete a snapshot repository
[expedient.elastic.ece_traffic_ruleset](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.ece_traffic_ruleset_module.rst)|placeholder
[expedient.elastic.elastic_user](https://github.com/Expedient/ansible-collection-elastic/blob/main/docs/expedient.elastic.elastic_user_module.rst)|elastic user management

<!--end collection content-->

