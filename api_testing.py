import http.client

conn = http.client.HTTPSConnection("dev-op4dpb8txjx5ikl5.us.auth0.com")

payload = "{\"client_id\":\"rpLJXdxsMFs6ZExGZeU7ia9TrJL3ZhNh\",\"client_secret\":\"FnCn5coFxkBd0STQdq7ZrF74rWWIkegTOwFDieo-OBzBAxCPaPCNdelIoEcItW7S\",\"audience\":\"https://dev-op4dpb8txjx5ikl5.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))