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
        # Task 4 - VNet Peering (двосторонній)
        # Лінк з боку CoreServicesVnet: ManufacturingVnet-to-CoreServicesVnet
        f"az network vnet peering create -g {rg} -n ManufacturingVnet-to-CoreServicesVnet --vnet-name CoreServicesVnet --remote-vnet ManufacturingVnet --allow-vnet-access --allow-forwarded-traffic",
        # Лінк з боку ManufacturingVnet: CoreServicesVnet-to-ManufacturingVnet
        f"az network vnet peering create -g {rg} -n CoreServicesVnet-to-ManufacturingVnet --vnet-name ManufacturingVnet --remote-vnet CoreServicesVnet --allow-vnet-access --allow-forwarded-traffic",

        # Task 6 - UDR: таблиця маршрутів rt-CoreServices
        f"az network route-table create -g {rg} -n rt-CoreServices --disable-bgp-route-propagation true",
        # Маршрут PerimetertoCore: через NVA 10.0.1.7
        f"az network route-table route create -g {rg} --route-table-name rt-CoreServices -n PerimetertoCore --address-prefix 10.0.0.0/16 --next-hop-type VirtualAppliance --next-hop-ip-address 10.0.1.7",
        # Прив'язка таблиці до підмережі perimeter
        f"az network vnet subnet update -g {rg} --vnet-name CoreServicesVnet -n perimeter --route-table rt-CoreServices",
    ]

    for cmd in commands:
        run_command(cmd)

if __name__ == "__main__":
    main()
