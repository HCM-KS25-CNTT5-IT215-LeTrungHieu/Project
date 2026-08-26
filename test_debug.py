import json
import time
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def req(method, endpoint, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = f"Bearer {token}"
    req_data = json.dumps(data).encode('utf-8') if data else None
    r = urllib.request.Request(BASE_URL+endpoint, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as res:
            return res.getcode(), json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return e.code, e.read().decode('utf-8')

# Login admin
st, res = req("POST", "/auth/login", {"email": "admin@example.com", "password": "admin123"})
admin_token = res['data']['access_token']

# Create project
st, res = req("POST", "/projects", {"name": "Debug Proj", "description": "123"}, admin_token)
print("Create Project:", st, res)
pid = res['data']['id']

time.sleep(1)

# Get project
st, res = req("GET", f"/projects/{pid}", token=admin_token)
print("Get Project:", st, res)

# List projects
st, res = req("GET", f"/projects", token=admin_token)
print("List Projects:", st, res)
