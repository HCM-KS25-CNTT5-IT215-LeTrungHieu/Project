import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            res = json.loads(body) if body else {}
            assert isinstance(res, dict)
            return status, res
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            res = json.loads(body)
            assert isinstance(res, dict)
            return e.code, res
        except Exception:  # noqa: BLE001
            return e.code, body
    except urllib.error.URLError as e:
        print(f"Error connecting to {url}: {e}")
        return 0, str(e)


tests_passed = 0
tests_total = 0


def run_test(
    name, expected_status, method, endpoint, data=None, token=None, extract_fn=None
):
    global tests_passed, tests_total
    tests_total += 1
    status, body = make_request(method, endpoint, data, token)
    if status == expected_status:
        print(f"✅ PASS: {name} (Got {status})")
        tests_passed += 1
        if extract_fn:
            return extract_fn(body)
    else:
        print(f"❌ FAIL: {name} (Expected {expected_status}, Got {status})")
        print(f"   Response: {body}")
        if extract_fn:
            return None


print("=== BẮT ĐẦU TEST TOÀN BỘ API ===")


status, res = make_request(
    "POST", "/auth/login", {"email": "admin@example.com", "password": "admin123"}
)
admin_token = res["data"]["access_token"] if status == 200 else None

status, res = make_request(
    "POST", "/auth/login", {"email": "user@example.com", "password": "user123"}
)
user_token = res["data"]["access_token"] if status == 200 else None


outsider_email = "outsider@example.com"
make_request(
    "POST",
    "/auth/register",
    {"email": outsider_email, "full_name": "Outsider", "password": "pass"},
)
status, res = make_request(
    "POST", "/auth/login", {"email": outsider_email, "password": "pass"}
)
outsider_token = res["data"]["access_token"] if status == 200 else None


status, res = make_request("GET", "/users/me", token=outsider_token)
outsider_id = res["data"]["id"] if status == 200 else 999


status, res = make_request("GET", "/users/me", token=user_token)
user_id = res["data"]["id"] if status == 200 else 999


status, res = make_request("GET", "/users/me", token=admin_token)
admin_id = res["data"]["id"] if status == 200 else 999


run_test("GET /users/me (Valid Token)", 200, "GET", "/users/me", token=admin_token)
run_test("GET /users/me (No Token)", 401, "GET", "/users/me")
run_test("GET /users (Admin)", 200, "GET", "/users", token=admin_token)
run_test("GET /users (Normal User)", 403, "GET", "/users", token=user_token)


project_id = run_test(
    "POST /projects (Create Project)",
    201,
    "POST",
    "/projects",
    {"name": "Test Proj", "description": "Test"},
    token=admin_token,
    extract_fn=lambda b: b["data"]["id"],
)

run_test("GET /projects (List my projects)", 200, "GET", "/projects", token=admin_token)
run_test(
    "GET /projects/{id} (Member access)",
    200,
    "GET",
    f"/projects/{project_id}",
    token=admin_token,
)
run_test(
    "GET /projects/{id} (Outsider access)",
    403,
    "GET",
    f"/projects/{project_id}",
    token=outsider_token,
)

run_test(
    "PATCH /projects/{id} (Owner update)",
    200,
    "PATCH",
    f"/projects/{project_id}",
    {"name": "Updated Proj"},
    token=admin_token,
)
run_test(
    "PATCH /projects/{id} (Member update)",
    403,
    "PATCH",
    f"/projects/{project_id}",
    {"name": "Hacked"},
    token=user_token,
)


run_test(
    "POST /projects/{id}/members (Owner adds member)",
    201,
    "POST",
    f"/projects/{project_id}/members",
    {"user_id": user_id, "role": "MEMBER"},
    token=admin_token,
)
run_test(
    "POST /projects/{id}/members (Add existing member)",
    400,
    "POST",
    f"/projects/{project_id}/members",
    {"user_id": user_id, "role": "MEMBER"},
    token=admin_token,
)
run_test(
    "POST /projects/{id}/members (Member adds member)",
    403,
    "POST",
    f"/projects/{project_id}/members",
    {"user_id": outsider_id, "role": "MEMBER"},
    token=user_token,
)

run_test(
    "GET /projects/{id}/members (Member lists members)",
    200,
    "GET",
    f"/projects/{project_id}/members",
    token=user_token,
)
run_test(
    "GET /projects/{id}/members (Outsider lists members)",
    403,
    "GET",
    f"/projects/{project_id}/members",
    token=outsider_token,
)

run_test(
    "DELETE /projects/{id}/members/{uid} (Member deletes another)",
    403,
    "DELETE",
    f"/projects/{project_id}/members/{admin_id}",
    token=user_token,
)


task_id = run_test(
    "POST /projects/{id}/tasks (Member creates task)",
    201,
    "POST",
    f"/projects/{project_id}/tasks",
    {"title": "Task 1", "description": "Desc"},
    token=admin_token,
    extract_fn=lambda b: b["data"]["id"],
)
run_test(
    "POST /projects/{id}/tasks (Assign to outsider)",
    400,
    "POST",
    f"/projects/{project_id}/tasks",
    {"title": "Task 2", "assignee_id": outsider_id},
    token=admin_token,
)
run_test(
    "POST /projects/{id}/tasks (Outsider creates task)",
    403,
    "POST",
    f"/projects/{project_id}/tasks",
    {"title": "Task 3"},
    token=outsider_token,
)

run_test(
    "GET /projects/{id}/tasks (List tasks)",
    200,
    "GET",
    f"/projects/{project_id}/tasks",
    token=admin_token,
)
run_test(
    "GET /tasks/{id} (Get detail)", 200, "GET", f"/tasks/{task_id}", token=user_token
)

run_test(
    "PATCH /tasks/{id} (Assignee updates)",
    200,
    "PATCH",
    f"/tasks/{task_id}",
    {"status": "IN_PROGRESS"},
    token=admin_token,
)


run_test(
    "GET /projects/{id}/activity-logs (Member views logs)",
    200,
    "GET",
    f"/projects/{project_id}/activity-logs",
    token=user_token,
)
run_test(
    "GET /projects/{id}/activity-logs (Outsider views logs)",
    403,
    "GET",
    f"/projects/{project_id}/activity-logs",
    token=outsider_token,
)


run_test(
    "DELETE /projects/{id} (Member deletes project)",
    403,
    "DELETE",
    f"/projects/{project_id}",
    token=user_token,
)
run_test(
    "DELETE /projects/{id} (Owner deletes project)",
    200,
    "DELETE",
    f"/projects/{project_id}",
    token=admin_token,
)

print(f"\n=== HOÀN TẤT: PASS {tests_passed}/{tests_total} ===")
