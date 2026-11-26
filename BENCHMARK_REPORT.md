# Day 14 — Benchmark & Observability Report

**Ngày chạy:** 2026-11-26  
**Môi trường:** Windows + Docker Desktop/WSL2 Ubuntu 24.04; Docker Engine 29.x; Locust 100 users, headless 120 giây cho mỗi lượt scale.

## 1. SLO của agent

| SLI | SLO | Lý do |
|---|---:|---|
| p95 latency `/ask` | < 500 ms | Ngưỡng mục tiêu cho phần lớn request; p95/p99 phơi bày tail latency bị average che khuất. |
| Error rate `/ask` | < 2% | Ngưỡng mục tiêu cho lỗi tạm thời trong benchmark. |
| Accuracy golden dataset | ≥ 90% | Quality gate tối thiểu của bài lab. |

## 2. Benchmark hiệu năng (develop, load_test.py)

Nguồn: các JSON trong `reports/`. Các lượt độc lập có độ dao động; cột SLO theo hai điều kiện p95 < 500 ms và lỗi < 2%.

### 2.1 Concurrency vs latency (agent v2)

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 3.54 | 191.5 | 1669.2 | 1715.1 | 0.67% | FAIL |
| 10 | 44.63 | 190.1 | 219.6 | 344.3 | 2.33% | FAIL |
| 50 | 104.93 | 197.1 | 250.1 | 1695.4 | 1.33% | PASS |
| 100 | 66.39 | 330.1 | 2794.1 | 2985.9 | 0.00% | FAIL |

RPS tăng mạnh từ concurrency 1 đến 50, nhưng không tăng tuyến tính và giảm ở 100. Tail latency tăng rõ ở 1/50/100 do các request chậm hiếm gặp; các lần chạy là mẫu nhỏ, độc lập và không đủ để kết luận một throughput ổn định duy nhất. Tài nguyên CPU, event loop, giới hạn connection và latency mock LLM cùng ảnh hưởng kết quả.

### 2.2 Tail latency

| `MOCK_SLOW_RATE` | avg (ms) | p95 (ms) | p99 (ms) |
|---:|---:|---:|---:|
| 0 | 191.3 | 218.5 | 228.4 |
| 0.03 | 248.1 | 221.4 | 1703.9 |
| 0.1 | 350.2 | 1694.8 | 1710.3 |

Request chậm tác động mạnh lên p99 trước khi ảnh hưởng p95; ở slow rate 0.1, p95 cũng vượt SLO. Average không cho biết nhóm request đuôi chậm trải nghiệm ra sao nên SLO cần theo percentile.

## 3. Benchmark chất lượng (golden dataset, 23 câu)

| Chỉ số | Agent v1 | Agent v2 | Agent v2 sau sửa KB |
|---|---:|---:|---:|
| Accuracy | 4.35% (1/23) | 91.30% (21/23) | 100% (23/23) |
| Avg tokens / câu | 56.7 | 109.0 | 114.4 |
| Tổng cost (USD) | 0.000398 | 0.000759 | 0.000797 |
| Cost / câu đúng (USD) | 0.00039795 | 0.00003616 | 0.00003465 |
| Quality gate | FAIL | PASS | PASS |

| ID | Thiếu trong câu trả lời v2 | Sửa |
|---|---|---|
| security-02 | Nội dung về lưu trữ API key an toàn | Bổ sung mục knowledge base về secrets/security. |
| scaling-03 | Nội dung về scale ngang và state dùng chung | Bổ sung mục knowledge base về Redis/shared state. |

v2 dùng nhiều token và có tổng cost cao hơn v1, nhưng độ chính xác và hiệu quả cost trên mỗi câu đúng tốt hơn đáng kể. Sửa KB nâng accuracy từ 91.3% lên 100%, không có regression trên bộ 23 câu.

## 4. Observability stack (production)

### 4.1 Bằng chứng ảnh

Chưa có ảnh PNG được lưu trong `screenshots/`. Dashboard Grafana đã được xem trực tiếp khi có tải, nhưng chưa xuất thành file; Jaeger trace screenshots và ảnh trang Prometheus cũng chưa được lưu. Không đánh dấu các ảnh này là đã nộp.

### 4.2 Thí nghiệm gây lỗi

Lượt Locust gây lỗi gần nhất chạy với cấu hình lỗi/độ trễ bật đồng thời: 13,275 request tổng, 2,424 lỗi (18.26%), p50 190 ms, p95 1700 ms. Do A và B chạy chung, không thể quy thời gian phát hiện riêng cho từng thay đổi. Khi kiểm tra sau lượt chạy, Prometheus còn alert `LLMCostBurnRateHigh` ở trạng thái firing, activeAt `2026-11-26T14:08:32.571501534Z`; API không còn trả alert lỗi/latency đang firing. Thời gian từ lúc đổi cấu hình đến firing của A/B không được lưu chính xác nên không suy đoán.

Lượt kiểm tra local bổ sung ngày 2026-11-26 dùng 25 users trong 90 giây: 1,245 request, 226 lỗi (18.15%), p95 1700 ms. Trên trang Prometheus, `AgentHighErrorRate` và `AgentHighLatencyP95` ở trạng thái **pending**, chưa xác nhận firing; lượt chạy này không đủ lâu để kết luận alert firing.

| # | Thay đổi | Quan sát được |
|---|---|---|
| A | `MOCK_ERROR_RATE=0.2` | Chạy cùng B; lượt chaos có error rate 18.26%, nhưng không có thời điểm firing riêng được lưu. |
| B | `MOCK_SLOW_RATE=0.3` | Chạy cùng A; p95 của lượt chaos khoảng 1700 ms; không có thời điểm firing riêng được lưu. |
| C | `LLM_MODEL=mock-llm-large` | Chưa có lượt thử riêng được lưu. |
| D | Pause một instance | Chưa có lượt thử riêng được lưu. |
| E | `AGENT_VERSION=v1` | Chưa có lượt thử riêng được lưu. |

Để phát hiện lỗi chất lượng kiểu E, chạy golden dataset/evaluation định kỳ và chặn deploy khi accuracy hoặc regression vượt ngưỡng; metric hạ tầng đơn thuần không đo được nội dung câu trả lời.

### 4.3 Debug bằng trace

Đã lưu log mẫu ở `screenshots/observability-run-evidence.txt`. Một event lỗi `llm_error` có trace ID `9247434abc17702d6147b21d6cf5f8a8` (upstream 503); một request chậm có trace ID `15081fdef98c8864d259825fb46bfab2`, `llm_ms=1663.4`. Đây là ID trong log agent; Jaeger UI/API không trả danh sách trace trước khi stack bị dừng, nên chưa xác minh được trace, tổng duration và event exception trong Jaeger. Ảnh Jaeger trace chưa được lưu.

## 5. Benchmark scaling (production, Locust headless, 100 users, 2 phút)

Nguồn: hàng `Aggregated` trong `benchmark-results/scale_1_stats.csv` và `scale_3_stats.csv`.

| Số instance | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---:|---:|---:|---:|---:|---|
| 1 | 65.305 | 190 | 330 | 1700 | 73 / 7777 (0.94%) |
| 3 | 65.287 | 190 | 290 | 1700 | 62 / 7762 (0.80%) |

Ba instance giảm p95 khoảng 40 ms và giảm tỷ lệ lỗi nhẹ, nhưng RPS gần như không đổi. Đây là dấu hiệu nút thắt nằm ngoài số lượng agent instance (ví dụ mock LLM, CPU hoặc giới hạn tài nguyên chung); cần thêm telemetry/tăng tải có kiểm soát để định vị chính xác.

## 6. Kết luận

1. p95/p99 quan trọng vì request chậm có thể bị average che khuất.
2. Tăng concurrency hoặc số instance không đảm bảo throughput tăng tuyến tính; cần đo bottleneck.
3. Benchmark quality cần golden dataset cùng quality gate để phát hiện regression mà metric hạ tầng không thấy.

Nếu chạy production thật, nên bổ sung metric/alert về token/cost theo model và tenant (tránh label cardinality cao), queue/connection pool saturation, timeout/retry, tỷ lệ câu trả lời đạt quality gate và tuổi của dữ liệu knowledge base.
