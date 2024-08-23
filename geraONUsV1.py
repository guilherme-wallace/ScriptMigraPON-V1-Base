import os

# Arquivo contendo a lista de ONUs
ONU_FILE = 'onu_huawei.txt'

# Arquivo contendo as descrições das ONUs
ONU_FILE_DESC = 'onu_huawei_desc.txt'

# VLAN do serviço
VLAN_IN = 1904

# VLAN de saída para ONU
VLAN_OUT = 1904

# Inicializa variáveis
PON_ZERA = "0"
ONU_ID = 0
ONT_SRV_PROF = 1904
ONT_LIN_PROF = 1904
GEM_PORT = 126

LISTA_ONUS = 'lista_onus_hw.txt'
LISTA_SRV = 'lista_onus_hw_srv.txt'

# Limpa os arquivos de saída
open(LISTA_ONUS, 'w').close()
open(LISTA_SRV, 'w').close()

# Lê o arquivo de ONUs e armazena o número total de ONUs
with open(ONU_FILE, 'r') as f:
    onu_lines = f.readlines()

total_onus = [line.split()[3] for line in onu_lines if "Ont SN" in line]

# Processa cada ONU
for ONU_SN in total_onus:
    # Busca a linha que contém o ONU_SN
    sn_index = next(i for i, line in enumerate(onu_lines) if ONU_SN in line)
    
    # Procura pela linha contendo "F/S/P" nas linhas anteriores
    porta_pon_line = None
    for i in range(sn_index, -1, -1):
        if "F/S/P" in onu_lines[i]:
            porta_pon_line = onu_lines[i]
            break
    
    if porta_pon_line:
        porta_pon = porta_pon_line.split()[2] if len(porta_pon_line.split()) >= 3 else None
        if porta_pon and '/' in porta_pon:
            pon_id = porta_pon.split('/')[2]
        else:
            print(f"Erro: Porta PON inválida para ONU {ONU_SN}")
            print(f"Conteúdo da linha: {porta_pon_line.strip()}")
            continue
    else:
        print(f"Erro: Linha da Porta PON não encontrada para ONU {ONU_SN}")
        continue

    modelo_line = next((line for line in onu_lines if ONU_SN in line), None)
    modelo = modelo_line.split()[3] if modelo_line and len(modelo_line.split()) >= 4 else None

    if modelo in ["SH1020W", "FD511G-X", "HG9"]:
        onu_oper = "ROUTER"
    else:
        onu_oper = "BRIDGE"

    with open(ONU_FILE_DESC, 'r') as f:
        onu_desc_lines = f.readlines()
    
    onu_desc = next((line.split()[5] for line in onu_desc_lines if ONU_SN[8:16] in line), ONU_SN)

    with open(LISTA_ONUS, 'a') as lista_onus_file:
        lista_onus_file.write(f'ont add {pon_id} {ONU_ID} sn-auth {ONU_SN} omci ont-lineprofile-id {ONT_LIN_PROF} ont-srvprofile-id {ONT_SRV_PROF} desc "{onu_desc}"\n\n')
        
        if onu_oper == "ROUTER":
            for i in range(1, 5):
                lista_onus_file.write(f'ont port route {pon_id} {ONU_ID} eth {i} enable\n\n')
        else:
            lista_onus_file.write(f'ont port native-vlan {pon_id} {ONU_ID} eth 1 vlan {VLAN_OUT} priority 0\n\n')

    with open(LISTA_SRV, 'a') as lista_srv_file:
        if onu_oper == "ROUTER":
            lista_srv_file.write(f'service-port vlan {VLAN_OUT} gpon {porta_pon} ont {ONU_ID} gemport {GEM_PORT} multi-service user-vlan untagged tag-transform default\n\n')
        else:
            lista_srv_file.write(f'service-port vlan {VLAN_IN} gpon {porta_pon} ont {ONU_ID} gemport {GEM_PORT} multi-service user-vlan {VLAN_OUT} tag-transform translate\n\n')

    ONU_ID += 1

# Exibe o conteúdo dos arquivos gerados
with open(LISTA_ONUS, 'r') as lista_onus_file:
    print(lista_onus_file.read())

print()

with open(LISTA_SRV, 'r') as lista_srv_file:
    print(lista_srv_file.read())
