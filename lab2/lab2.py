import subprocess
import json
import sys
import time
import os

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


new_group = run_az_command([
    "az", "ad", "group", "create",
    "--display-name", "helpdesk",
    "--mail-nickname", "helpdesk",
    "--description", "Help Desk Support Group"
])
group_id = new_group["id"]


time.sleep(30)

mg_name = "az104-mg1"
mg_scope = f"/providers/Microsoft.Management/managementGroups/{mg_name}"

run_az_command([
    "az", "account", "management-group", "create",
    "--name", mg_name,
    "--display-name", mg_name
], return_json=False)


run_az_command([
    "az", "role", "assignment", "create",
    "--assignee-object-id", group_id,
    "--assignee-principal-type", "Group",
    "--role", "Virtual Machine Contributor",
    "--scope", mg_scope
], return_json=False)


custom_role_def = {
    "Name": "Custom Support Request",
    "IsCustom": True,
    "Description": "A custom contributor role for support requests.",
    "Actions": [
        "Microsoft.Authorization/*/read",
        "Microsoft.Resources/subscriptions/read",
        "Microsoft.Support/*"
    ],
    "NotActions": [
        "Microsoft.Support/register/action"
    ],
    "AssignableScopes": [
        mg_scope
    ]
}

role_file_path = "custom_role.json"
with open(role_file_path, "w") as f:
    json.dump(custom_role_def, f, indent=4)

run_az_command([
    "az", "role", "definition", "create",
    "--role-definition", role_file_path
], return_json=False)

if os.path.exists(role_file_path):
    os.remove(role_file_path)
