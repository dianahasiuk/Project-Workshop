import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)

def get_output(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip().strip('"')

def main():
    rg_name = "az104-rg6"
    appgw_name = "az104-06-appgw"
    pip_name = "az104-06-pip5"
    vnet_name = "az104-06-vnet"
    subnet_name = "subnet-appgw"

    ip_vm0 = get_output(f"az vm show -d -g {rg_name} -n az104-06-vm0 --query privateIps -o tsv")
    ip_vm1 = get_output(f"az vm show -d -g {rg_name} -n az104-06-vm1 --query privateIps -o tsv")

    if not ip_vm0 or not ip_vm1:
        print("Помилка: Неможливо отримати IP-адреси віртуальних машин.")
        sys.exit(1)

    # Task 3 - Application Gateway
    subprocess.run(
        f"az network public-ip create -g {rg_name} -n {pip_name} --sku Standard --allocation-method Static",
        shell=True, capture_output=True
    )

    appgw_cmd = (
        f"az network application-gateway create -g {rg_name} -n {appgw_name} --sku Standard_v2 "
        f"--vnet-name {vnet_name} --subnet {subnet_name} --public-ip-address {pip_name} "
        f"--capacity 2 --frontend-port 80 --http-settings-port 80 "
        f"--http-settings-protocol Http --priority 100"
    )
    subprocess.run(appgw_cmd, shell=True, capture_output=True)

    # Backend pools: pool-image → vm0 (зображення), pool-video → vm1 (відео)
    subprocess.run(f"az network application-gateway address-pool create -g {rg_name} --gateway-name {appgw_name} -n pool-image --servers {ip_vm0}", shell=True)
    subprocess.run(f"az network application-gateway address-pool create -g {rg_name} --gateway-name {appgw_name} -n pool-video --servers {ip_vm1}", shell=True)

    # Path-based routing: /image/* → pool-image, /video/* → pool-video
    subprocess.run(
        f"az network application-gateway url-path-map create -g {rg_name} --gateway-name {appgw_name} "
        f"-n url-map --paths /image/* --address-pool pool-image "
        f"--default-address-pool appGatewayBackendPool --default-http-settings appGatewayBackendHttpSettings "
        f"--http-settings appGatewayBackendHttpSettings --rule-name rule-image",
        shell=True
    )
    subprocess.run(
        f"az network application-gateway url-path-map rule create -g {rg_name} --gateway-name {appgw_name} "
        f"--path-map-name url-map -n rule-video --paths /video/* "
        f"--address-pool pool-video --http-settings appGatewayBackendHttpSettings",
        shell=True
    )

    run_command(
        f"az network application-gateway rule update -g {rg_name} --gateway-name {appgw_name} "
        f"-n rule1 --rule-type PathBasedRouting --url-path-map url-map"
    )

    appgw_ip = get_output(f"az network public-ip show -g {rg_name} -n {pip_name} --query ipAddress -o tsv")
    print(f"Головна: http://{appgw_ip}")
    print(f"Зображення (vm0): http://{appgw_ip}/image/iisstart.htm")
    print(f"Відео (vm1): http://{appgw_ip}/video/iisstart.htm")

if __name__ == "__main__":
    main()
