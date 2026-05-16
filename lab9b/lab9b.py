import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip().strip('"')

def main():
    rg_name = "az104-rg9"
    location = "westeurope"
    container_name = "az104-c1"
    dns_name_label = "az104-c1-diana"

    
    subprocess.run(
        f"az group create --name {rg_name} --location {location}",
        shell=True, capture_output=True
    )

    create_cmd = (
        f"az container create --resource-group {rg_name} --name {container_name} "
        f"--image mcr.microsoft.com/azuredocs/aci-helloworld:latest "
        f"--dns-name-label {dns_name_label} --ports 80 --os-type Linux "
        f"--cpu 1 --memory 1.5"
    )
    run_command(create_cmd)

    fqdn = run_command(
        f"az container show --resource-group {rg_name} --name {container_name} "
        f"--query ipAddress.fqdn --output tsv"
    )
    print(f"Welcome to Azure Container Instance: http://{fqdn}")

   
    logs = run_command(
        f"az container logs --resource-group {rg_name} --name {container_name}"
    )
    print("\n--- Logs ---")
    print(logs)

if __name__ == "__main__":
    main()
