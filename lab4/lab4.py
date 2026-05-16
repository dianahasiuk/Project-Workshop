import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{command}\nДеталі:\n{result.stderr}")
        sys.exit(1)

def main():
    rg_name = "az104-rg4"
    location = "uaenorth"

    
    run_command(f"az group create -n {rg_name} -l {location}")
    run_command(f"az network vnet create -g {rg_name} -n CoreServicesVnet --address-prefix 10.20.0.0/16 --subnet-name SharedServicesSubnet --subnet-prefix 10.20.10.0/24")
    run_command(f"az network vnet subnet create -g {rg_name} --vnet-name CoreServicesVnet -n DatabaseSubnet --address-prefix 10.20.20.0/24")

  
    template_file = "az104-04-template.json"
    parameters_file = "az104-04-parameters.json"
    run_command(f"az deployment group create -g {rg_name} --template-file {template_file} --parameters @{parameters_file}")

   
    run_command(f"az network asg create -g {rg_name} -n asg-web -l {location}")
    run_command(f"az network nsg create -g {rg_name} -n myNSGSecure -l {location}")
    run_command(f"az network vnet subnet update -g {rg_name} --vnet-name CoreServicesVnet -n SharedServicesSubnet --network-security-group myNSGSecure")
    run_command(f"az network nsg rule create -g {rg_name} --nsg-name myNSGSecure -n AllowASG --priority 100 --source-asgs asg-web --source-port-ranges '*' --destination-address-prefixes '*' --destination-port-ranges 80 443 --protocol Tcp --access Allow --direction Inbound")
    run_command(f"az network nsg rule create -g {rg_name} --nsg-name myNSGSecure -n DenyInternetOutbound --priority 4096 --source-address-prefixes '*' --source-port-ranges '*' --destination-address-prefixes Internet --destination-port-ranges '*' --protocol '*' --access Deny --direction Outbound")

   
    public_dns = "contosolab04.com"
    private_dns = "private.contoso.com"

    run_command(f"az network dns zone create -g {rg_name} -n {public_dns}")
    run_command(f"az network dns record-set a add-record -g {rg_name} --zone-name {public_dns} --record-set-name www --ipv4-address 10.1.1.4")
    run_command(f"az network private-dns zone create -g {rg_name} -n {private_dns}")
    run_command(f"az network private-dns link vnet create -g {rg_name} --zone-name {private_dns} -n manufacturing-link --virtual-network ManufacturingVnet --registration-enabled false")
    run_command(f"az network private-dns record-set a add-record -g {rg_name} --zone-name {private_dns} --record-set-name sensorvm --ipv4-address 10.1.1.4")

if __name__ == "__main__":
    main()
