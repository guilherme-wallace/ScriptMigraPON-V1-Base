import paramiko
import time
from dadosConexaoOLTs import *

USE_OLT = "OLT-SEA01"
    
if (USE_OLT == "OLT-SEA01"):
    ip = ip_SEA01
if (USE_OLT == "OLT-SEA03"):
    ip = ip_SEA03
if (USE_OLT == "OLT-VTA01"):
    ip = ip_VTA01
if (USE_OLT == "OLT-VTA02"):
    ip = ip_VTA02
if (USE_OLT == "OLT-VVA01"):
    ip = ip_VVA01
if (USE_OLT == "OLT-VVA03"):
    ip = ip_VVA03   
if (USE_OLT == "OLT-CCA01"):
    ip = ip_CCA01


# Dados de acesso SSH
hostname = ip
username = user
password = user_password

# Comandos para a OLT
commands = [
    "enable",
    "config",
    "display ont info summary 0/1/0 | no-more",
    "\n"
]

def ssh_connect_and_execute(hostname, username, password, commands, delay=0.5, timeout=10):
    # Cria um cliente SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conecta ao host via SSH com timeout
        client.connect(hostname, username=username, password=password, timeout=timeout)

        # Cria um shell interativo
        ssh_shell = client.invoke_shell()

        # Executa os comandos no shell
        for command in commands:
            ssh_shell.send(command + '\n')
            time.sleep(delay)  # Aguarda um tempo para o comando ser processado

            # Aguarda até que o comando seja processado
            output = ""
            end_time = time.time() + timeout
            while time.time() < end_time:
                if ssh_shell.recv_ready():
                    output += ssh_shell.recv(4096).decode('utf-8')
                else:
                    time.sleep(0.5)  # Aguarda um pouco antes de verificar novamente

            print(output)

    except Exception as e:
        print(f"Erro ao conectar ou executar comandos: {e}")
    finally:
        # Fecha a conexão SSH
        client.close()

# Executa a função
ssh_connect_and_execute(hostname, username, password, commands, delay=0.5, timeout=20)