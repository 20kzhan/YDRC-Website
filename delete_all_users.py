from os import environ as env
import aiohttp
import asyncio

import requests, time

MANAGEMENT_API_KEY = ""
API_KEY_EXPIRATION = 86400
last_renewal_time = 0

async def get_api_key():
    global MANAGEMENT_API_KEY, last_renewal_time
    current_time = time.time()
    
    if (current_time - last_renewal_time) > API_KEY_EXPIRATION or MANAGEMENT_API_KEY is None:
        payload = {
            "grant_type": "client_credentials",
            "client_id": env.get("MTM_CLIENT_ID"),
            "client_secret": env.get("MTM_CLIENT_SECRET"),
            "audience": f"https://{env.get('AUTH0_DOMAIN')}/api/v2/"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://{env.get('AUTH0_DOMAIN')}/oauth/token", data=payload) as response:
                if response.status == 200:
                    json_response = await response.json()
                    MANAGEMENT_API_KEY = json_response.get("access_token")
                    last_renewal_time = current_time
                else:
                    raise Exception("Failed to renew API key")

    return MANAGEMENT_API_KEY

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://dev-op4dpb8txjx5ikl5.us.auth0.com/api/v2/users", headers={
            "Authorization": f"Bearer {MANAGEMENT_API_KEY}"
        }) as resp:
            users = await resp.json()
            print(users)

        for user in users:
            print(user)
            user_id = user['user_id']
            async with session.delete(f"https://dev-op4dpb8txjx5ikl5.us.auth0.com/api/v2/users/{user_id}", headers={
                "Authorization": f"Bearer {MANAGEMENT_API_KEY}"
            }) as resp:
                await asyncio.sleep(3)
                if resp.status != 204:
                    print(f"Failed to delete user {user_id}")
                    print(await resp.text())
                    return
                print(f"Deleted user {user_id}")

input("Are you sure you want to delete all users? Press Enter to continue...")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
