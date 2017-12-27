import json
import os
import requests


IFTTT_KEY = os.environ["IFTTT_KEY"]
ECOBEE_API_KEY = os.environ["ECOBEE_API_KEY"]
ECOBEE_REFRESH_TOKEN_FILE = os.environ["ECOBEE_REFRESH_TOKEN_FILE"]
CURRENT_STATUS_FILE = os.environ["CURRENT_STATUS_FILE"]

# Open the refresh_token file
with open(ECOBEE_REFRESH_TOKEN_FILE) as f:
    refresh_token = f.read().strip()


# Sort out the refresh token.
refresh_token_data = {
  "grant_type": "refresh_token",
  "code": refresh_token,
  "client_id": ECOBEE_API_KEY,

}

tokens = requests.post("https://api.ecobee.com/token", data=refresh_token_data).json()

new_refresh_token = tokens["refresh_token"]
with open(ECOBEE_REFRESH_TOKEN_FILE, "w") as f:
    f.write(new_refresh_token)


# Now poll the thermostat

headers = {
    "Content-Type": "text/json",
    "Authorization": "Bearer %s" % tokens["access_token"],
}

selection = {
    "selection": {
        "selectionType": "registered",
        "selectionMatch":"",
        "includeEquipmentStatus":True
    }
}

status = requests.get("https://api.ecobee.com/1/thermostatSummary?json=%s" % json.dumps(selection), headers=headers).json()

thermostat_status = status["statusList"][0].split(":")[1].split(",")

if "auxHeat1" in thermostat_status:
    new_status = "heat"
else:
    new_status = "off"


# Now check the current status
with open(CURRENT_STATUS_FILE) as f:
    old_status = f.read().strip()


if old_status != new_status:
    url = "https://maker.ifttt.com/trigger/warmulator_%s/with/key/%s" % (new_status, IFTTT_KEY)
    print(url)
    requests.post(url)

    with open(CURRENT_STATUS_FILE, "w") as f:
        f.write(new_status)


print(new_status)
