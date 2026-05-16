import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)

def main():
    rg_name = "az104-rg6"
    location = "eastus"
    vm_size = "Standard_D2s_v3"
    admin_user = "localadmin"
    admin_pass = "P9kL2xM7vQ4nB1cW"
    image = "Win2019Datacenter"

    run_command(f"az group create --name {rg_name} --location {location}")
    run_command(f"az network nsg create -g {rg_name} -n az104-06-nsg")
    run_command(f"az network nsg rule create -g {rg_name} --nsg-name az104-06-nsg -n allow-web --priority 1000 --destination-port-ranges 80 3389 --protocol Tcp --access Allow")

    run_command(f"az network vnet create -g {rg_name} -n az104-06-vnet --address-prefix 10.60.0.0/16 --subnet-name subnet0 --subnet-prefix 10.60.0.0/24")
    run_command(f"az network vnet subnet create -g {rg_name} --vnet-name az104-06-vnet -n subnet1 --address-prefix 10.60.1.0/24")
    run_command(f"az network vnet subnet create -g {rg_name} --vnet-name az104-06-vnet -n subnet-appgw --address-prefix 10.60.3.224/27")

    run_command(f"az vm create -g {rg_name} -n az104-06-vm0 --image {image} --vnet-name az104-06-vnet --subnet subnet0 --nsg az104-06-nsg --admin-username {admin_user} --admin-password \"{admin_pass}\" --size {vm_size} --no-wait")
    run_command(f"az vm create -g {rg_name} -n az104-06-vm1 --image {image} --vnet-name az104-06-vnet --subnet subnet1 --nsg az104-06-nsg --admin-username {admin_user} --admin-password \"{admin_pass}\" --size {vm_size}")

    ps0 = (
        "Install-WindowsFeature -name Web-Server; "
        "Remove-Item C:\\inetpub\\wwwroot\\iisstart.htm; "
        "Add-Content -Path C:\\inetpub\\wwwroot\\iisstart.htm -Value 'Hello World from az104-06-vm0'; "
        "New-Item -Path C:\\inetpub\\wwwroot -Name image -ItemType Directory; "
        "Add-Content -Path C:\\inetpub\\wwwroot\\image\\iisstart.htm -Value 'Image from az104-06-vm0'"
    )
    ps1 = (
        "Install-WindowsFeature -name Web-Server; "
        "Remove-Item C:\\inetpub\\wwwroot\\iisstart.htm; "
        "Add-Content -Path C:\\inetpub\\wwwroot\\iisstart.htm -Value 'Hello World from az104-06-vm1'; "
        "New-Item -Path C:\\inetpub\\wwwroot -Name video -ItemType Directory; "
        "Add-Content -Path C:\\inetpub\\wwwroot\\video\\iisstart.htm -Value 'Video from az104-06-vm1'"
    )

    run_command(f"az vm run-command invoke -g {rg_name} -n az104-06-vm0 --command-id RunPowerShellScript --scripts \"{ps0}\"")
    run_command(f"az vm run-command invoke -g {rg_name} -n az104-06-vm1 --command-id RunPowerShellScript --scripts \"{ps1}\"")

if __name__ == "__main__":
    main()
