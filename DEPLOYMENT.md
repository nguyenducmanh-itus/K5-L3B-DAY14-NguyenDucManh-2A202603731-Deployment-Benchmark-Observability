# Deployment status — Day 14

## Trạng thái

**Chưa deploy lên Railway hoặc Render.** Không có URL public để kiểm tra và không ghi URL mẫu như kết quả thật. Workspace có cấu hình sẵn `railway.toml` và `render.yaml`; checker xác nhận cấu hình deploy/health check hợp lệ.

Để hoàn tất phần này, chủ tài khoản cần tạo service từ repo này, nối Redis, cấu hình các biến bí mật trong dashboard của nền tảng (không commit `.env`/API key), rồi chạy các kiểm tra dưới đây và lưu URL/ảnh thật:

| Kiểm tra | Kết quả |
|---|---|
| `GET /health` | Chưa chạy trên cloud |
| `GET /ready` | Chưa chạy trên cloud |
| `POST /ask` không có `X-API-Key` → 401 | Chưa chạy trên cloud |
| `POST /ask` có API key hợp lệ → 200 | Chưa chạy trên cloud |

Ảnh cần chụp sau khi deploy: `screenshots/dashboard.png`, `screenshots/running.png`, `screenshots/test.png`. Không lưu API key/token trong ảnh hoặc báo cáo.

## Local verification

Part 6 đã được kiểm tra local bằng Docker/WSL2: `PASS 12/12`, 43/43 checks; image 54 MB. Output: `06-lab-complete/check_production_ready_output.txt`.
