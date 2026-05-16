import json
import requests
from azure.identity import DefaultAzureCredential

RG_NAME = "az104-rg3"
LOCATION = "uaenorth"

def get_arm_headers():
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_subscription_id(headers):
    url = "https://management.azure.com/subscriptions?api-version=2020-01-01"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        subs = response.json().get("value", [])
        if subs:
            return subs[0].get("subscriptionId")
    print(f"[ERROR] Не вдалося отримати subscriptionId: {response.status_code}")
    return None

def get_arm_template():
    return {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "disk_name": {"type": "string"},
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]"
            },
            "sku_name": {"type": "string", "defaultValue": "Standard_LRS"},
            "diskSizeGb": {"type": "int", "defaultValue": 32}
        },
        "resources": [
            {
                "type": "Microsoft.Compute/disks",
                "apiVersion": "2023-04-02",
                "name": "[parameters('disk_name')]",
                "location": "[parameters('location')]",
                "sku": {
                    "name": "[parameters('sku_name')]"
                },
                "properties": {
                    "creationData": {"createOption": "Empty"},
                    "diskSizeGB": "[parameters('diskSizeGb')]"
                }
            }
        ]
    }

def deploy_disk_via_template(sub_id, headers, disk_name, sku_name="Standard_LRS"):
    deployment_name = f"deploy-{disk_name}"
    url = (
        f"https://management.azure.com/subscriptions/{sub_id}"
        f"/resourcegroups/{RG_NAME}/providers/Microsoft.Resources"
        f"/deployments/{deployment_name}?api-version=2021-04-01"
    )
    payload = {
        "properties": {
            "mode": "Incremental",
            "template": get_arm_template(),
            "parameters": {
                "disk_name": {"value": disk_name},
                "sku_name": {"value": sku_name}
            }
        }
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print(f"[OK] Розгортання '{disk_name}' запущено")
    else:
        print(f"[ERROR] '{disk_name}': {response.status_code} — {response.text}")

def main():
    headers = get_arm_headers()
    sub_id = get_subscription_id(headers)
    if not sub_id:
        return

    # Завдання 1-3: Створення resource group
    rg_url = (
        f"https://management.azure.com/subscriptions/{sub_id}"
        f"/resourcegroups/{RG_NAME}?api-version=2021-04-01"
    )
    res = requests.put(rg_url, headers=headers, json={"location": LOCATION})
    if res.status_code not in [200, 201]:
        print(f"[ERROR] Resource group: {res.status_code} — {res.text}")
        return
    print(f"[OK] Resource group '{RG_NAME}' готова")

    # Завдання 1: az104-disk1 (Standard HDD, 32 GiB) — базове розгортання
    deploy_disk_via_template(sub_id, headers, "az104-disk1")

    # Завдання 2: az104-disk2 — повторне розгортання через редагований шаблон
    deploy_disk_via_template(sub_id, headers, "az104-disk2")

    # Завдання 3: az104-disk3 — розгортання через PowerShell (Cloud Shell)
    deploy_disk_via_template(sub_id, headers, "az104-disk3")

    # Завдання 4: az104-disk4 — розгортання через CLI (Bash)
    deploy_disk_via_template(sub_id, headers, "az104-disk4")

    # Завдання 5: az104-disk5 — розгортання через Bicep (StandardSSD)
    deploy_disk_via_template(sub_id, headers, "az104-disk5", sku_name="StandardSSD_LRS")

if __name__ == "__main__":
    main()
