import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Помилка:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    rg_name = "az104-rg9"
    location = "westeurope"         
    asp_name = "ASP-az104rg9-a3b9"
    app_name = "az104-diana"
    slot_name = "staging"

   
    run_command(f"az group create --name {rg_name} --location {location}")
    run_command(
        f"az appservice plan create -g {rg_name} -n {asp_name} "
        f"--location {location} --sku B1 --is-linux"
    )
    run_command(
        f"az webapp create -g {rg_name} -p {asp_name} -n {app_name} "
        f"--runtime \"PHP|8.2\""
    )

    
    run_command(f"az appservice plan update -g {rg_name} -n {asp_name} --sku S1")


    run_command(
        f"az webapp deployment slot create -g {rg_name} -n {app_name} --slot {slot_name}"
    )


    run_command(
        f"az webapp deployment source config -g {rg_name} -n {app_name} "
        f"--slot {slot_name} "
        f"--repo-url https://github.com/Azure-Samples/php-docs-hello-world "
        f"--branch master --manual-integration"
    )


    run_command(
        f"az webapp deployment slot swap -g {rg_name} -n {app_name} "
        f"--slot {slot_name} --target-slot production"
    )


    run_command(
        f"az monitor autoscale create -g {rg_name} "
        f"--resource {asp_name} "
        f"--resource-type Microsoft.Web/serverfarms "
        f"-n {app_name}-autoscale "
        f"--min-count 1 --max-count 2 --count 1 "
        f"-l {location}"
    )

    print(f"Production: https://{app_name}.azurewebsites.net")
    print(f"Staging:    https://{app_name}-{slot_name}.azurewebsites.net")

if __name__ == "__main__":
    main()
