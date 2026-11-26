# Day 14 Lab — Mission Answers (bản tham chiếu)

> Bản đối chiếu do AI hỗ trợ. Kết quả chạy thật được ghi theo artifacts trong workspace; cloud deployment và một số ảnh chưa hoàn tất, xem `DEPLOYMENT.md` và `SUBMISSION_CHECKLIST.md`.

## Part 1 — Localhost vs Production

### Exercise 1.1 — Anti-patterns trong bản develop

1. API key và thông tin kết nối được ghi trực tiếp trong mã nguồn; nếu đẩy repo lên nơi công khai thì bí mật có thể bị lộ.
2. Bật `DEBUG`/reload cho môi trường chạy thật, làm tăng rủi ro và không phù hợp production.
3. Ghi log bằng `print`, thậm chí in cả key; log khó lọc và có thể làm lộ thông tin nhạy cảm.
4. Không có health/readiness check nên nền tảng khó biết tiến trình còn sống và đã sẵn sàng chưa.
5. Bind vào `localhost` và cố định cổng 8000; container/cloud thường cần bind `0.0.0.0` và đọc `PORT` từ môi trường.
6. Không xác thực request, không giới hạn tốc độ/chi phí; người ngoài có thể gọi tự do.
7. Không quản lý graceful shutdown, có thể cắt request đang xử lý khi tiến trình dừng.

### Exercise 1.2 — Chạy bản develop

**Chưa lưu được kết quả chạy Part 1.2** (HTTP status/response). Lệnh theo đề cho WSL2: `curl -X POST "http://localhost:8000/ask?question=Hello"`.

### Exercise 1.3 — So sánh

| Khía cạnh | Develop | Production | Vì sao cần |
|---|---|---|---|
| Bí mật | Giá trị mẫu hardcode | Đọc từ env/secret store | Tránh commit/lộ thông tin |
| Cấu hình | Giá trị cố định | Biến môi trường | Cùng image chạy được ở nhiều môi trường |
| Logging | `print`, nội dung tùy ý | Log có cấu trúc | Tìm kiếm và cảnh báo dễ hơn |
| Network/port | Localhost, port cố định | `0.0.0.0`, `PORT` | Nhận traffic từ container/platform |
| Health | Thiếu hoặc sơ sài | `/health`, `/ready` | Orchestrator biết sống và sẵn sàng |
| Dừng tiến trình | Không chờ request | Lifespan/SIGTERM graceful | Tránh request đang chạy bị mất |
| Bảo vệ API | Không có | API key, rate limit, budget | Hạn chế truy cập, lạm dụng và chi phí |

## Part 2 — Docker

### Exercise 2.1 — Dockerfile

1. Base image: image Python slim phù hợp vì nhỏ hơn bản đầy đủ mà vẫn có runtime cần thiết.
2. `WORKDIR` đặt thư mục làm việc mặc định bên trong image.
3. Copy `requirements.txt` và cài dependencies trước khi copy source để tận dụng cache layer khi chỉ đổi mã nguồn.
4. Multi-stage build bỏ compiler/build tooling khỏi stage runtime; runtime chỉ nhận dependencies đã cài và source cần thiết.

### Exercise 2.2–2.4 — Chạy image/Compose

Checker Part 6 xác nhận production image build được, kích thước 54 MB và `GET /health` trả 200. Chưa lưu số đo image develop hoặc output test Nginx riêng, nên chưa tính phần trăm chênh lệch.

Sơ đồ stack 2.4: Client → Nginx (port công khai) → agent; Nginx chuyển tiếp request đến agent trong mạng Compose. Điền cổng/service thực tế theo compose và output của bạn.

## Part 3 — Cloud Deployment

### Railway và Render

Bản tham chiếu Part 6 có `railway.toml` dùng Dockerfile builder và health check `/health`; `render.yaml` mô tả web service Docker, health check và Redis. Railway khai báo build/deploy trong TOML; Render khai báo Blueprint gồm service và biến môi trường trong YAML. Cả hai phải nhận `PORT` do nền tảng cấp và lấy API key/Redis URL từ biến môi trường/secret.

Chưa deploy Railway/Render, chưa có URL public và chưa chạy 4 HTTP checks trên cloud. Cấu hình Railway/Render có trong repo và được checker xác nhận. Xem `DEPLOYMENT.md`.

### Exercise 3.3 — Cloud Build / Cloud Run

Pipeline Cloud Build chạy test trước. Khi test thành công, nó build Docker image gắn tag theo commit và `latest`, đẩy image lên registry rồi deploy image theo commit lên Cloud Run ở `asia-southeast1`. `service.yaml` mô tả service công khai, giới hạn CPU/RAM/concurrency và autoscaling, cấu hình secret cùng health probes. Trong cấu hình hiện tại, service chạy tối thiểu 1 và tối đa 10 instance.

## Part 4 — API Security

### Exercise 4.1–4.3

API key nên được truyền trong header, so sánh an toàn với secret cấu hình và trả 401 nếu thiếu/sai. JWT mang claims và thời hạn nên có thể hết hạn/xác minh chữ ký; API key thường là credential ổn định, ít metadata hơn và cần rotate/revoke riêng. Rate limit giới hạn số request trong khoảng thời gian; vượt ngưỡng trả 429 và `Retry-After`.

Checker thực tế xác nhận API key thiếu/sai → 401, key đúng → 200, vượt giới hạn → 429 sau 5 request thành công; trạng thái giới hạn vẫn còn sau khi restart agent nhờ Redis. Raw `curl -i` chưa được lưu.

### Exercise 4.4 — Cost guard

Cost guard cộng dồn chi phí ước tính theo token ở Redis và từ chối request mới bằng 402 khi tổng vượt ngân sách đã đặt. Rate limit và cost guard bổ sung cho nhau: một cái chặn tốc độ gọi, cái kia chặn mức chi tiêu tích lũy.

## Part 5 — Scaling & Reliability

`/health` là liveness: process còn chạy thì trả 200, kể cả Redis lỗi để tránh restart vòng lặp. `/ready` phản ánh khả năng nhận traffic: trả 503 nếu Redis chưa sẵn sàng. State trong RAM không được chia sẻ giữa replicas và mất khi restart; Redis cung cấp state dùng chung. Load balancer phân phối request cho nhiều instance, còn graceful shutdown cho phép hoàn tất request đang xử lý trước khi thoát.

Checker thực tế xác nhận `/health` vẫn 200 khi Redis mất kết nối, `/ready` trả 503, state rate-limit trong Redis tồn tại sau restart, và graceful shutdown hoàn tất với exit code 0 trong 1.2 giây. CSV scale 1/3 production nằm ở `benchmark-results/`; chưa lưu output riêng của `test_stateless.py`.

## Part 6 — Final Project

Mã nguồn tham chiếu nằm trong `06-lab-complete/`. Checker đã chạy từ WSL2/Docker: **PASS 12/12 tiêu chí, 43/43 checks**, image 54 MB; output đầy đủ ở `06-lab-complete/check_production_ready_output.txt`.

## Part 7 — Benchmark & Observability

### Phân tích cần đối chiếu

- p95/p99 cho thấy trải nghiệm ở nhóm request chậm; trung bình có thể che mất tail latency.
- RPS không tăng tuyến tính vô hạn vì có giới hạn CPU/event loop, connection pool, network và latency mock LLM.
- `MOCK_SLOW_RATE` tăng thường tác động rõ nhất lên p99 (và dần p95 nếu tỉ lệ request chậm đủ lớn).
- v2 dùng retrieval nên có thể tăng chất lượng nhưng thêm latency/tokens; cần cân cost trên mỗi câu đúng và regression.
- Exit code 1 từ `run_eval.py` nên làm CI job thất bại để chặn merge/deploy.
- Metrics hạ tầng không tự phát hiện câu trả lời sai; cần eval/golden dataset hoặc quality metric.
- Prometheus pull đơn giản và phù hợp service ổn định; autoscale-to-zero cần cân nhắc push/managed collection hoặc synthetic checks.
- Label `user_id` gây cardinality cao, tốn RAM và làm Prometheus khó vận hành; chỉ dùng label có tập giá trị nhỏ.
- Sampling trace giảm chi phí/storage nhưng có thể bỏ lỡ sự cố hiếm; có thể ưu tiên giữ lỗi/trace chậm.
- `for: 0s` dễ alert do spike; `for: 30m` báo quá trễ.

Các bảng eval/load/scale đã điền trong `BENCHMARK_REPORT.md` từ JSON/CSV thật. A/B bật cùng lúc nên không có alert timing độc lập; lần thử ngắn sau reboot cho thấy error/latency alert ở trạng thái pending, không xác nhận firing. Log mẫu có trace ID nhưng Jaeger screenshot/lookup chưa lưu được.

## AI log

- Yêu cầu: nhờ AI đọc yêu cầu lab, triển khai bản tham chiếu Part 6 và tổng hợp danh sách file nộp.
- Hỗ trợ nhận được: giải thích tiêu chí, sửa cấu hình/code production agent, tạo bản nháp câu trả lời và checklist file.
- Học viên cần đọc, hiểu và tự đối chiếu mã cùng kết quả. Một số bước chưa chạy được (cloud deployment, test riêng Part 1.2/Nginx/stateless và ảnh); xem checklist trước khi nộp.

## Kết quả chạy thực tế bổ sung (2026-11-26)

- Checker Part 6: **PASS 12/12 tiêu chí, 43/43 checks**; graceful shutdown exit code 0 trong 1.2 giây.
- Eval: v1 1/23 (4.35%); v2 21/23 (91.30%); v2 sau sửa KB 23/23 (100%).
- Locust scale 1/3: CSV trong `benchmark-results/`; các số p50/p95/p99/RPS/failures tổng hợp ở `BENCHMARK_REPORT.md`.
- Observability evidence: log mẫu với trace ID lỗi/chậm ở `screenshots/observability-run-evidence.txt`; chưa có ảnh PNG dùng được.
