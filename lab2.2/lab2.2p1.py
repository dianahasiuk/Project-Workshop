import subprocess
import json
import sys

def run_az_command(cmd, return_json=True):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        print(f"Помилка: {result.stderr}")
        sys.exit(1)
    if return_json and result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout.strip()
    return result.stdout.strip()

sub_info = run_az_command(["az", "account", "show"])
sub_id = sub_info["id"]

rg_name = "az104-rg2"
rg_scope = f"/subscriptions/{sub_id}/resourceGroups/{rg_name}"
location = "eastus"

# Завдання 1: Створення ресурсної групи з тегом
run_az_command([
    "az", "group", "create",
    "--name", rg_name,
    "--location", location,
    "--tags", "Cost Center=000"
], return_json=False)

# Завдання 2: Призначення політики автоматичного успадкування тегу
run_az_command([
    "az", "policy", "assignment", "create",
    "--name", "inherit-tag-policy",
    "--display-name", "Inherit the Cost Center tag from the resource group",
    "--scope", rg_scope,
    "--policy", "ea3f2387-9b95-492a-a190-fcdc54f7b070",
    "--params", '{"tagName": {"value": "Cost Center"}}',
    "--assign-identity",
    "--location", location
], return_json=False)

# Завдання 3: Налаштування блокування ресурсу
run_az_command([
    "az", "lock", "create",
    "--name", "PreventDeleteLock",
    "--lock-type", "CanNotDelete",
    "--resource-group", rg_name,
    "--notes", "Prevent accidental deletion of the resource group"
], return_json=False)
