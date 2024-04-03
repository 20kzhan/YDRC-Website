<<<<<<< HEAD
import http.client

conn = http.client.HTTPSConnection("dev-op4dpb8txjx5ikl5.us.auth0.com")

payload = "{\"client_id\":\"rpLJXdxsMFs6ZExGZeU7ia9TrJL3ZhNh\",\"client_secret\":\"FnCn5coFxkBd0STQdq7ZrF74rWWIkegTOwFDieo-OBzBAxCPaPCNdelIoEcItW7S\",\"audience\":\"https://dev-op4dpb8txjx5ikl5.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

=======
import http.client

conn = http.client.HTTPSConnection("dev-op4dpb8txjx5ikl5.us.auth0.com")

payload = "{\"client_id\":\"rpLJXdxsMFs6ZExGZeU7ia9TrJL3ZhNh\",\"client_secret\":\"FnCn5coFxkBd0STQdq7ZrF74rWWIkegTOwFDieo-OBzBAxCPaPCNdelIoEcItW7S\",\"audience\":\"https://dev-op4dpb8txjx5ikl5.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

>>>>>>> f0664b25e0e2c0621c944bed919f34efc1cc8918
print(data.decode("utf-8"))