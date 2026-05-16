import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)

def main():
    rg = "az104-rg5"
    loc = "eastus"
    user = "localadmin"
    pwd = "P9kL2xM7vQ4nB1cW"
    image = "MicrosoftWindowsServer:WindowsServer:2025-datacenter-g2:latest"

    commands = [
        f"az group create -n {rg} -l {loc}",
        f"az network nsg create -g {rg} -n CoreServices-nsg",
        f"az network nsg rule create -g {rg} --nsg-name CoreServices-nsg -n Allow-RDP --priority 1000 --destination-port-ranges 3389 --protocol Tcp --access Allow --direction Inbound",
        f"az network vnet create -g {rg} -n CoreServicesVnet --address-prefix 10.0.0.0/16 --subnet-name Core --subnet-prefix 10.0.0.0/24",
        f"az network vnet subnet create -g {rg} --vnet-name CoreServicesVnet -n perimeter --address-prefixes 10.0.1.0/24",
        f"az network public-ip create -g {rg} -n CoreServicesVM-pip --sku Standard",
        f"az network nic create -g {rg} -n CoreServicesVM-nic --vnet-name CoreServicesVnet --subnet Core --public-ip-address CoreServicesVM-pip --network-security-group CoreServices-nsg",
        f"az vm create -g {rg} -n CoreServicesVM --nics CoreServicesVM-nic --image {image} --admin-username {user} --admin-password \"{pwd}\" --size Standard_D2s_v3 --no-wait",
        f"az network nsg create -g {rg} -n Manufacturing-nsg",
        f"az network nsg rule create -g {rg} --nsg-name Manufacturing-nsg -n Allow-RDP --priority 1000 --destination-port-ranges 3389 --protocol Tcp --access Allow --direction Inbound",
        f"az network vnet create -g {rg} -n ManufacturingVnet --address-prefix 172.16.0.0/16 --subnet-name Manufacturing --subnet-prefix 172.16.0.0/24",
        f"az network public-ip create -g {rg} -n ManufacturingVM-pip --sku Standard",
        f"az network nic create -g {rg} -n ManufacturingVM-nic --vnet-name ManufacturingVnet --subnet Manufacturing --public-ip-address ManufacturingVM-pip --network-security-group Manufacturing-nsg",
        f"az vm create -g {rg} -n ManufacturingVM --nics ManufacturingVM-nic --image {image} --admin-username {user} --admin-password \"{pwd}\" --size Standard_D2s_v3 --no-wait",
    ]

    for cmd in commands:
        run_command(cmd)

if __name__ == "__main__":
    main()
