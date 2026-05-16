import subprocess
import json
import sys

GUEST_EMAIL = "hasukdiana@gmail.com"
GUEST_NAME = "diana hasiuk"
PASSWORD = "P9kL2xM7vQ4nB1cW"
TENANT_DOMAIN = "hasukdianagmail.onmicrosoft.com"

def graph_request(method, endpoint, body=None, ignore_errors=False):
    url = f"https://graph.microsoft.com/v1.0{endpoint}"
    cmd = ["az", "rest", "--method", method, "--url", url]
    if body is not None:
        cmd.extend(["--headers", "Content-Type=application/json", "--body", json.dumps(body)])
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        if ignore_errors:
            return None
        print(f"Помилка Graph API ({method} {endpoint}):\n{result.stderr}")
        sys.exit(1)
    if result.stdout.strip():
        return json.loads(result.stdout)
    return None

me_data = graph_request("GET", "/me")
my_id = me_data["id"]

upn_user1 = f"az104-user1@{TENANT_DOMAIN}"

check_user = graph_request("GET", f"/users?$filter=userPrincipalName eq '{upn_user1}'")
if check_user.get("value"):
    user1_id = check_user["value"][0]["id"]
else:
    user_body = {
        "accountEnabled": True,
        "displayName": "az104-user1",
        "mailNickname": "az104user1",
        "userPrincipalName": upn_user1,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": PASSWORD
        },
        "jobTitle": "IT Lab Administrator",
        "department": "IT",
        "usageLocation": "US"
    }
    new_user = graph_request("POST", "/users", user_body)
    user1_id = new_user["id"]

invite_body = {
    "invitedUserEmailAddress": GUEST_EMAIL,
    "inviteRedirectUrl": "https://portal.azure.com",
    "sendInvitationMessage": True,
    "invitedUserMessageInfo": {
        "customizedMessageBody": "Welcome to Azure and our group project"
    },
    "invitedUserDisplayName": GUEST_NAME
}
invite_result = graph_request("POST", "/invitations", invite_body)
guest_user_id = invite_result["invitedUser"]["id"]

guest_update_body = {
    "jobTitle": "IT Lab Administrator",
    "department": "IT",
    "usageLocation": "US"
}
graph_request("PATCH", f"/users/{guest_user_id}", guest_update_body)

check_group = graph_request("GET", "/groups?$filter=displayName eq 'IT Lab Administrators'")
if check_group.get("value"):
    group_id = check_group["value"][0]["id"]
else:
    group_body = {
        "displayName": "IT Lab Administrators",
        "mailEnabled": False,
        "mailNickname": "ITLabAdmins",
        "securityEnabled": True,
        "description": "Administrators that manage the IT lab"
    }
    new_group = graph_request("POST", "/groups", group_body)
    group_id = new_group["id"]

owner_body = {
    "@odata.id": f"https://graph.microsoft.com/v1.0/users/{my_id}"
}
graph_request("POST", f"/groups/{group_id}/owners/$ref", owner_body, ignore_errors=True)

member1_body = {
    "@odata.id": f"https://graph.microsoft.com/v1.0/users/{user1_id}"
}
graph_request("POST", f"/groups/{group_id}/members/$ref", member1_body, ignore_errors=True)

member2_body = {
    "@odata.id": f"https://graph.microsoft.com/v1.0/users/{guest_user_id}"
}
graph_request("POST", f"/groups/{group_id}/members/$ref", member2_body, ignore_errors=True)
