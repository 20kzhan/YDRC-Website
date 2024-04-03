import time
import requests
from os import environ as env

MANAGEMENT_API_KEY = None
API_KEY_EXPIRATION = 86400
last_renewal_time = 0

def get_api_key():
    global MANAGEMENT_API_KEY, last_renewal_time
    current_time = time.time()
    
    if (current_time - last_renewal_time) > API_KEY_EXPIRATION or MANAGEMENT_API_KEY is None:
        payload = {
            "grant_type": "client_credentials",
            "client_id": env.get("MTM_CLIENT_ID"),
            "client_secret": env.get("MTM_CLIENT_SECRET"),
            "audience": f"https://{env.get('AUTH0_DOMAIN')}/api/v2/"
        }

        response = requests.request("POST", f"https://{env.get('AUTH0_DOMAIN')}/oauth/token", data=payload)
        if response.status_code == 200:
            MANAGEMENT_API_KEY = response.json().get("access_token")
            last_renewal_time = current_time
        else:
            raise Exception("Failed to renew API key")

    return MANAGEMENT_API_KEY

if __name__ == "__main__":
    print(get_api_key())