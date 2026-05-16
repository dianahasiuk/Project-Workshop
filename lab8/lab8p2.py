import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка: {result.stderr}")
        sys.exit(1)

def main():
    rg_name = "az104-rg8"
    location = "austriaeast"
    admin_user = "localadmin"
    admin_pass = "P9kL2xM7vQ4nB1cW"
    image_urn = "MicrosoftWindowsServer:WindowsServer:2025-datacenter-g2:latest"

    # Task 3 - Створення VMSS vmss1 у трьох зонах (Zone 1, 2, 3)
    run_command(f"az network nsg create -g {rg_name} -n vmss1-nsg -l {location}")
    run_command(
        f"az network nsg rule create -g {rg_name} --nsg-name vmss1-nsg "
        f"-n allow-http --priority 1010 --destination-port-ranges 80 --protocol Tcp --access Allow"
    )
    run_command(
        f"az network vnet create -g {rg_name} -n vmss-vnet --address-prefix 10.82.0.0/20 "
        f"--subnet-name subnet0 --subnet-prefix 10.82.0.0/24 "
        f"--network-security-group vmss1-nsg -l {location}"
    )
    run_command(
        f"az vmss create -g {rg_name} -n vmss1 --image {image_urn} "
        f"--vm-sku Standard_D2s_v3 --zones 1 2 3 "
        f"--admin-username {admin_user} --admin-password \"{admin_pass}\" "
        f"--vnet-name vmss-vnet --subnet subnet0 --lb vmss-lb "
        f"--instance-count 2 --upgrade-policy-mode manual -l {location}"
    )

    # Task 4 - Автоматичне масштабування: Custom autoscale, Scale based on metric
    # Ліміти: мін. 2, макс. 10, за замовчуванням 2
    run_command(
        f"az monitor autoscale create -g {rg_name} -n vmss1-autoscale "
        f"--resource vmss1 --resource-type Microsoft.Compute/virtualMachineScaleSets "
        f"--min-count 2 --max-count 10 --count 2 -l {location}"
    )

    # Scale Out: CPU > 70% протягом 10 хв → збільшити на 50%
    run_command(
        f"az monitor autoscale rule create -g {rg_name} --autoscale-name vmss1-autoscale "
        f"--scale out 50% --condition \"Percentage CPU > 70 avg 10m\""
    )

    # Scale In: CPU < 30% протягом 10 хв → зменшити на 50%
    run_command(
        f"az monitor autoscale rule create -g {rg_name} --autoscale-name vmss1-autoscale "
        f"--scale in 50% --condition \"Percentage CPU < 30 avg 10m\""
    )

if __name__ == "__main__":
    main()
