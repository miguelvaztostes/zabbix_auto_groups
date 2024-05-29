---
- name: Configure Zabbix Server API Authentication
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Set credentials to access Zabbix Server API
      set_fact:
        ansible_user: Admin
        ansible_httpapi_pass: "YCv4!y_M),nu'C-"

    - name: Set API token
      set_fact:
        ansible_zabbix_auth_key: 1c9823eb2aaf6039865f46ad5e72a5fa3b73eb6b49c77a60cd431a780970e923

- name: Create host groups
  hosts: Zabbix Server
  gather_facts: false
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 8080
    ansible_httpapi_use_ssl: false
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url: 'http://localhost:8080'
  tasks:
    - name: Create host groups
      community.zabbix.zabbix_group:
        state: present
        host_groups:
          - Teste 1 
          - Teste 2
