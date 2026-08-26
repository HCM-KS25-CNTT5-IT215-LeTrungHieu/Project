import json
import urllib.request

r = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=json.dumps({"email": "admin@example.com", "password": "admin123"}).encode(), headers={'Content-Type': 'application/json'}, method="POST")
token = json.loads(urllib.request.urlopen(r).read().decode())['data']['access_token']

r2 = urllib.request.Request("http://127.0.0.1:8000/projects", data=json.dumps({"name": "No BG", "description": "123"}).encode(), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method="POST")
print(urllib.request.urlopen(r2).read().decode())
