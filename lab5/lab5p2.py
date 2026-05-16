import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)

def main():
    rg = "az104-rg5"

    commands = [
      
        f"az network vnet peering create -g {rg} -n ManufacturingVnet-to-CoreServicesVnet --vnet-name CoreServicesVnet --remote-vnet ManufacturingVnet --allow-vnet-access --allow-forwarded-traffic",
      
        f"az network vnet peering create -g {rg} -n CoreServicesVnet-to-ManufacturingVnet --vnet-name ManufacturingVnet --remote-vnet CoreServicesVnet --allow-vnet-access --allow-forwarded-traffic",

       
        f"az network route-table create -g {rg} -n rt-CoreServices --disable-bgp-route-propagation true",
       
        f"az network route-table route create -g {rg} --route-table-name rt-CoreServices -n PerimetertoCore --address-prefix 10.0.0.0/16 --next-hop-type VirtualAppliance --next-hop-ip-address 10.0.1.7",
        
        f"az network vnet subnet update -g {rg} --vnet-name CoreServicesVnet -n perimeter --route-table rt-CoreServices",
    ]

    for cmd in commands:
        run_command(cmd)

if __name__ == "__main__":
    main()
