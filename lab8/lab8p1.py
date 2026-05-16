import subprocess
import sys
import time

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{command}\nДеталі:\n{result.stderr}")
        sys.exit(1)

def main():
    rg_name = "az104-rg8"
    location = "austriaeast"
    admin_user = "localadmin"
    admin_pass = "P9kL2xM7vQ4nB1cW"
    image_urn = "MicrosoftWindowsServer:WindowsServer:2025-datacenter-g2:latest"

    run_command(f"az group create -n {rg_name} -l {location}")
    run_command(
        f"az vm create -g {rg_name} -n az104-vm1 --image {image_urn} "
        f"--size Standard_D2s_v3 --zone 1 --admin-username {admin_user} "
        f"--admin-password \"{admin_pass}\" --public-ip-sku Standard --no-wait"
    )
    run_command(
        f"az vm create -g {rg_name} -n az104-vm2 --image {image_urn} "
        f"--size Standard_D2s_v3 --zone 2 --admin-username {admin_user} "
        f"--admin-password \"{admin_pass}\" --public-ip-sku Standard"
    )

    run_command(f"az vm resize -g {rg_name} -n az104-vm1 --size Standard_D2ds_v4")

    run_command(f"az disk create -g {rg_name} -n vm1-disk1 --size-gb 32 --sku Standard_LRS --zone 1")
    run_command(f"az vm disk attach -g {rg_name} --vm-name az104-vm1 --name vm1-disk1")
    time.sleep(10)

    run_command(f"az vm disk detach -g {rg_name} --vm-name az104-vm1 --name vm1-disk1")
    time.sleep(15)

    run_command(f"az disk update -g {rg_name} -n vm1-disk1 --sku StandardSSD_LRS")
    run_command(f"az vm disk attach -g {rg_name} --vm-name az104-vm1 --name vm1-disk1")

if __name__ == "__main__":
    main()
