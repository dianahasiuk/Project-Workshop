import subprocess
import json
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)

def get_json_output(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def main():
    rg_name = "az104-rg6"

    # Task 2 - Azure Load Balancer
    # Frontend IP: az104-fe зі статичним публічним IP az104-lbpip
    run_command(f"az network public-ip create -g {rg_name} -n az104-lbpip --sku Standard --allocation-method Static")
    run_command(f"az network lb create -g {rg_name} -n az104-lb --sku Standard --public-ip-address az104-lbpip --frontend-ip-name az104-fe --backend-pool-name az104-be")

    # Health probe: az104-hp, TCP, порт 80, інтервал 5 сек
    run_command(f"az network lb probe create -g {rg_name} --lb-name az104-lb -n az104-hp --protocol tcp --port 80 --interval 5")

    # Правило балансування: az104-lbrule, TCP 80→80, без session persistence
    run_command(f"az network lb rule create -g {rg_name} --lb-name az104-lb -n az104-lbrule --protocol tcp --frontend-port 80 --backend-port 80 --frontend-ip-name az104-fe --backend-pool-name az104-be --probe-name az104-hp --disable-outbound-snat true")

    # Додавання vm0 та vm1 до backend pool az104-be
    for vm in ["az104-06-vm0", "az104-06-vm1"]:
        vm_info = get_json_output(f"az vm show -g {rg_name} -n {vm}")
        if vm_info and 'networkProfile' in vm_info:
            nic_id = vm_info['networkProfile']['networkInterfaces'][0]['id']
            nic_name = nic_id.split('/')[-1]
            nic_info = get_json_output(f"az network nic show -g {rg_name} -n {nic_name}")
            if nic_info and 'ipConfigurations' in nic_info:
                ipconf_name = nic_info['ipConfigurations'][0]['name']
                run_command(
                    f"az network nic ip-config address-pool add "
                    f"--address-pool az104-be --ip-config-name {ipconf_name} "
                    f"--nic-name {nic_name} -g {rg_name} --lb-name az104-lb"
                )

if __name__ == "__main__":
    main()
