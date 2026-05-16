import os
import subprocess
import json
import sys
import time
import requests
from datetime import datetime, timedelta, timezone

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

def get_output(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except Exception:
        sys.exit(1)

def main():
    rg_name = "az104-rg7"
    location = "swedencentral"
    sa_name = "az104stordh7"

    run_command(f"az group create --name {rg_name} --location {location}")
    run_command(
        f"az storage account create -n {sa_name} -g {rg_name} -l {location} "
        f"--sku Standard_GRS --public-network-access Disabled --allow-blob-public-access false"
    )

    my_ip = get_public_ip()
    run_command(f"az storage account update -n {sa_name} -g {rg_name} --public-network-access Enabled --default-action Deny")
    run_command(f"az storage account network-rule add -g {rg_name} --account-name {sa_name} --ip-address {my_ip}")
    time.sleep(15)

    policy_dict = {
        "rules": [{
            "enabled": True,
            "name": "Movetocool",
            "type": "Lifecycle",
            "definition": {
                "actions": {"baseBlob": {"tierToCool": {"daysAfterModificationGreaterThan": 30}}},
                "filters": {"blobTypes": ["blockBlob"]}
            }
        }]
    }
    with open("policy.json", "w") as f:
        json.dump(policy_dict, f)
    run_command(f"az storage account management-policy create --account-name {sa_name} -g {rg_name} --policy @policy.json")
    os.remove("policy.json")

    run_command(f"az storage container create --name data --account-name {sa_name} --auth-mode key")
    run_command(
        f"az storage container immutability-policy create --account-name {sa_name} "
        f"--container-name data --period 180 --resource-group {rg_name}"
    )

    blob_file = "security_test_file.txt"
    with open(blob_file, "w") as f:
        f.write("This is a highly secure test file for Azure Storage Lab.")
    run_command(
        f"az storage blob upload --account-name {sa_name} --container-name data "
        f"--name securitytest/{blob_file} --file {blob_file} --auth-mode key"
    )
    os.remove(blob_file)

    expiry = (datetime.now(timezone.utc) + timedelta(hours=48)).strftime('%Y-%m-%dT%H:%MZ')
    sas_token = get_output(
        f"az storage blob generate-sas --account-name {sa_name} -c data "
        f"-n securitytest/{blob_file} --permissions r --expiry {expiry} --auth-mode key -o tsv"
    )
    account_url = f"https://{sa_name}.blob.core.windows.net/data/securitytest/{blob_file}"
    print(f"SAS URL (48h): {account_url}?{sas_token}")

    run_command(
        f"az storage share-rm create -g {rg_name} --storage-account {sa_name} "
        f"--name share1 --quota 1024 --access-tier TransactionOptimized"
    )

    share_file = "file_for_share.txt"
    with open(share_file, "w") as f:
        f.write("A" * 50)
    run_command(
        f"az storage file upload --account-name {sa_name} --share-name share1 "
        f"--source {share_file} --auth-mode key"
    )
    os.remove(share_file)

    run_command(
        f"az network vnet create -g {rg_name} -n vnet1 "
        f"--address-prefix 10.50.0.0/16 --subnet-name default --subnet-prefix 10.50.1.0/24"
    )
    run_command(
        f"az network vnet subnet update -g {rg_name} --vnet-name vnet1 -n default "
        f"--service-endpoints Microsoft.Storage"
    )
    run_command(
        f"az storage account network-rule add -g {rg_name} --account-name {sa_name} "
        f"--vnet-name vnet1 --subnet default"
    )
    run_command(
        f"az storage account network-rule remove -g {rg_name} --account-name {sa_name} "
        f"--ip-address {my_ip}"
    )

if __name__ == "__main__":
    main()
