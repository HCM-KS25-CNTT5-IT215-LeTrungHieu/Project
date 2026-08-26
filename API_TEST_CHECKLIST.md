# Comprehensive API Test Checklist

Tài liệu này tổng hợp toàn bộ các Test Case (Trường hợp kiểm thử) cho toàn bộ API của dự án. Đánh dấu `[x]` hoặc tích vào ô trống sau khi hoàn thành test.

## 1. Authentication (`/auth`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/auth/register` | `POST` | Đăng ký thành công với thông tin hợp lệ <br> `{"email": "test@a.com", "password": "123", "full_name": "Test"}` | `201 Created` - Trả về thông tin User |
| [ ] | `/auth/register` | `POST` | Đăng ký với Email đã tồn tại | `400 Bad Request` |
| [ ] | `/auth/login` | `POST` | Đăng nhập thành công với email & password đúng <br> `{"email": "admin@example.com", "password": "admin123"}`| `200 OK` - Trả về `access_token` & `refresh_token` |
| [ ] | `/auth/login` | `POST` | Đăng nhập với sai mật khẩu hoặc sai email | `401 Unauthorized` |
| [ ] | `/auth/login` | `POST` | Đăng nhập với tài khoản bị khóa (`is_active=False`) | `400 Bad Request` |
| [ ] | `/auth/refresh` | `POST` | Refresh token hợp lệ <br> `{"refresh_token": "..."}` | `200 OK` - Trả về token mới |
| [ ] | `/auth/refresh` | `POST` | Refresh token đã bị thu hồi (`is_revoked=True`) hoặc hết hạn | `401 Unauthorized` |
| [ ] | `/auth/refresh` | `POST` | Refresh token không hợp lệ (sai signature) | `401 Unauthorized` |

---

## 2. Users (`/users`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/users/me` | `GET` | Lấy thông tin cá nhân với token hợp lệ | `200 OK` - Trả về profile |
| [ ] | `/users/me` | `GET` | Không gửi token hoặc token hết hạn | `401 Unauthorized` |
| [ ] | `/users` | `GET` | Lấy danh sách users bằng tài khoản Admin | `200 OK` - Có hỗ trợ `skip`, `limit`, `search` |
| [ ] | `/users` | `GET` | Lấy danh sách users bằng tài khoản thường | `403 Forbidden` |

---

## 3. Projects (`/projects`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/projects` | `POST` | Tạo project mới hợp lệ <br> `{"name": "Dự án A", "description": "Mô tả A"}`| `201 Created` - Người tạo tự động thành `OWNER` |
| [ ] | `/projects` | `GET` | Lấy danh sách project của bản thân (có tham gia) | `200 OK` - Hỗ trợ `search` |
| [ ] | `/projects/{id}` | `GET` | Lấy chi tiết project mà mình là thành viên | `200 OK` - Trả về chi tiết |
| [ ] | `/projects/{id}` | `GET` | Lấy chi tiết project mà mình KHÔNG là thành viên | `403 Forbidden` |
| [ ] | `/projects/{id}` | `PATCH` | Cập nhật project với vai trò `OWNER` <br> `{"name": "Updated"}` | `200 OK` - Trả về project cập nhật |
| [ ] | `/projects/{id}` | `PATCH` | Cập nhật project với vai trò `MEMBER` <br> `{"name": "Hacked"}`| `403 Forbidden` |
| [ ] | `/projects/{id}` | `DELETE` | Xóa project với vai trò `OWNER` | `200 OK` |
| [ ] | `/projects/{id}` | `DELETE` | Xóa project với vai trò `MEMBER` | `403 Forbidden` |

---

## 4. Project Members (`/projects/{id}/members`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/.../members` | `GET` | Lấy danh sách thành viên với tư cách là người trong dự án | `200 OK` |
| [ ] | `/.../members` | `GET` | Lấy danh sách thành viên với tư cách là người NGOÀI dự án | `403 Forbidden` |
| [ ] | `/.../members` | `POST` | Thêm user vào dự án với tư cách `OWNER` <br> `{"user_id": 2, "role": "MEMBER"}` | `201 Created` |
| [ ] | `/.../members` | `POST` | Thêm user vào dự án với tư cách `MEMBER` <br> `{"user_id": 3, "role": "MEMBER"}` | `403 Forbidden` |
| [ ] | `/.../members` | `POST` | Thêm user không tồn tại trong hệ thống | `404 Not Found` |
| [ ] | `/.../members` | `POST` | Thêm user ĐÃ LÀ THÀNH VIÊN vào dự án | `400 Bad Request` |
| [ ] | `/.../members/{uid}`| `DELETE` | `OWNER` xóa 1 thành viên bình thường | `200 OK` |
| [ ] | `/.../members/{uid}`| `DELETE` | `OWNER` tự xóa chính mình khỏi dự án | `400 Bad Request` |
| [ ] | `/.../members/{uid}`| `DELETE` | `MEMBER` cố gắng xóa thành viên khác | `403 Forbidden` |

---

## 5. Tasks (`/projects/{id}/tasks` & `/tasks/{id}`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/projects/{id}/tasks`| `POST` | Thành viên tạo Task mới (gán cho 1 thành viên khác)<br>`{"title": "Task 1", "description": "Fix bug", "assignee_id": 2}` | `201 Created` |
| [ ] | `/projects/{id}/tasks`| `POST` | Người ngoài dự án cố tình tạo Task | `403 Forbidden` |
| [ ] | `/projects/{id}/tasks`| `POST` | Tạo Task và gán (`assignee_id`) cho người KHÔNG thuộc dự án | `400 Bad Request` |
| [ ] | `/projects/{id}/tasks`| `GET` | Lấy danh sách Task (test Filter: `status`, `priority`) | `200 OK` |
| [ ] | `/projects/{id}/tasks`| `GET` | Lấy danh sách Task (test Pagination: `limit`, `offset`) | `200 OK` |
| [ ] | `/projects/{id}/tasks`| `GET` | Lấy danh sách Task (test Sort: `sort_by`, `sort_order`) | `200 OK` |
| [ ] | `/tasks/{id}` | `GET` | Xem chi tiết 1 Task trong dự án mình tham gia | `200 OK` |
| [ ] | `/tasks/{id}` | `PATCH` | `OWNER` hoặc `ASSIGNEE` cập nhật trạng thái Task<br>`{"status": "IN_PROGRESS"}` | `200 OK` |
| [ ] | `/tasks/{id}` | `PATCH` | `MEMBER` bình thường (không phải assignee) cập nhật Task | `403 Forbidden` |
| [ ] | `/tasks/{id}` | `PATCH` | `OWNER`/`ASSIGNEE` gán Task cho người ngoài dự án<br>`{"assignee_id": 999}` | `400 Bad Request` |
| [ ] | `/tasks/{id}` | `DELETE` | `OWNER` xóa Task | `200 OK` |
| [ ] | `/tasks/{id}` | `DELETE` | `MEMBER` bình thường xóa Task | `403 Forbidden` |

---

## 6. Activity Logs (`/projects/{id}/activity-logs`)

| Trạng thái | Endpoint | HTTP Method | Test Case | Expected Result |
| :---: | :--- | :---: | :--- | :--- |
| [ ] | `/.../activity-logs` | `GET` | Xem log khi là thành viên dự án | `200 OK` |
| [ ] | `/.../activity-logs` | `GET` | Xem log khi KHÔNG phải thành viên | `403 Forbidden` |
| [ ] | **N/A (Background)** | `System` | Tạo project -> kiểm tra có sinh ra log không | Tồn tại 1 record log |
| [ ] | **N/A (Background)** | `System` | Cập nhật project -> kiểm tra có sinh ra log không | Tồn tại 1 record log |
| [ ] | **N/A (Background)** | `System` | Thêm / Xóa member -> kiểm tra có sinh ra log không | Tồn tại 1 record log |
