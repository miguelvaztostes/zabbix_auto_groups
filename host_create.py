#!/usr/bin/python3

from zabbix_api import ZabbixAPI, Already_Exists
import csv
import sys
import getpass
import time

URL = sys.argv[1]
USERNAME = sys.argv[2]
PASSWORD = getpass.getpass("Digite a senha: ")

try:
    zapi = ZabbixAPI(URL, timeout=15)
    zapi.login(USERNAME, PASSWORD)
    print(f'Conectado na API do Zabbix, Versao Atual {zapi.api_version()}')
    print()
except Exception as err:
    print(f'Falha ao conectar na API do zabbix, erro: {err}')
    sys.exit(1)

# Função procura templates
def procurando_templates():
    id = zapi.template.get({
        "output": "extend",
    })
    if id:
        print("\n***Templates encontrados***")
        # Condição se é para procurar templateid e nome
        for x in id:
            print("TemplateID: {} - Nome: {}\n".format(x['templateid'], x['name']))
    else:
        print("\n***Templates não encontrados***")

procurando_templates()

# Variável armazena o id do template
template = list(map(int, input("\n(Para inserir mais de um template insira separado por espaço Ex: 10001 10277)\nInsira o templateid (Caso não deixe em branco)...: ").strip().split()))

while True:
    print("\nDeseja criar um grupo de host? \n1 - Sim \n2 - Não")
    opcao = input()
    if opcao == "1":
        NOMEGROUP = input("\nDigite o nome do grupo: ")
        try:
            zapi.hostgroup.create({
                "name": NOMEGROUP
            })
        except Already_Exists:
            print(f'Grupo {NOMEGROUP} já existe.')
        except Exception as err:
            print(f'Erro ao criar grupo: {err}')
    elif opcao == "2":
        break

def procurando_groupid():
    hostgroups = zapi.hostgroup.get({
        "output": ['name', 'groupid'],
        "sortfield": "name",
    })
    if hostgroups:
        print("\n***Groups encontrados***")
        print()
        for x in hostgroups:
            print("GroupID: {} - Nome: {}\n".format(x['groupid'], x['name']))
    else:
        print("\n***Groups não encontrados***")

procurando_groupid()

grupo = list(map(int, input("\n(Para inserir mais de um grupo insira separado por espaço Ex: 4 6)\nInsira o groupid....: ").strip().split()))

print('\n***Listando proxys***')
idproxy = zapi.proxy.get({
    "output": "extend",
    "sortfield": "host"
})
for x in idproxy:
    print("ProxyID: {} - Nome: {}\n".format(x['proxyid'], x['host']))
PROXY = input("\nDigite o proxyid caso não utilize insira 0: ")

print("\n***Tipos de interfaces possíveis: 1 - agent; 2 - SNMP***")
TYPEID = input("\nInsira o typeid...: ")

DESCRIPTION = input("\nDeseja inserir alguma descrição? Caso Não deixe em branco: ")
print('\nAguarde...')
time.sleep(2)

info_interfaces = {
    "1": {"type": "agent", "id": "1", "port": "10050"},
    "2": {"type": "SNMP", "id": "2", "port": "161"},
}

groupids = grupo
groups = [{"groupid": groupid} for groupid in groupids]

templateids = template
templates = [{"templateid": templateid} for templateid in templateids]

def create_host(nomes, host, ip):
    try:
        create_host = zapi.host.create({
            "groups": groups,
            "host": host,
            "name": nomes,
            "description": DESCRIPTION,
            "templates": templates,
            "proxy_hostid": PROXY if PROXY != '0' else None,
            "interfaces": [{
                "type": info_interfaces[TYPEID]['id'],
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": info_interfaces[TYPEID]['port'],
                "details": {
                    "version": 2,
                    "bulk": 1,
                    "community": "{$SNMP_COMMUNITY}" if TYPEID == "2" else ""
                }
            }]
        })
        print(f'Host cadastrado {host}')
    except Already_Exists:
        print(f'Host(s) já cadastrado {host}')
    except Exception as err:
        print(f'Falha ao cadastrar {host}: {err}')

with open('hosts.csv') as file:
    file_csv = csv.reader(file, delimiter=';')
    for [nome, hosts, ipaddress] in file_csv:
        create_host(nomes=nome, host=hosts, ip=ipaddress)

zapi.logout()
