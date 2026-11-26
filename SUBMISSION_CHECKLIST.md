# Checklist file nộp — Day 14 (K5)

## Đã chuẩn bị

- [x] `MISSION_ANSWERS.md` — câu trả lời tham chiếu, kết quả chạy thật và giới hạn còn thiếu được ghi rõ.
- [x] `DEPLOYMENT.md` — trạng thái cloud deploy và các kiểm tra cần hoàn tất; không bịa URL public.
- [x] `BENCHMARK_REPORT.md` — bảng benchmark được điền từ JSON/CSV đã chạy.
- [x] `06-lab-complete/` — code/config Part 6.
- [x] `06-lab-complete/check_production_ready_output.txt` — checker: PASS 12/12, 43/43 checks.
- [x] `reports/` — 3 eval JSON và 7 load JSON.
- [x] `benchmark-results/scale_1_stats.csv`, `benchmark-results/scale_3_stats.csv` — Locust scale 1 và 3 instances.
- [x] `evidence/observability-run-evidence.txt` — mẫu log có trace ID cho event lỗi và request chậm.
- [x] `evidence/chaos_90s_stats.csv` — lượt thử A/B đồng thời, 25 users/90 giây.

## Còn thiếu trước khi nộp toàn bộ lab

- [ ] Deploy thật lên Railway/Render, nối Redis và ghi URL public cùng kết quả 4 HTTP checks trong `DEPLOYMENT.md`.
- [ ] 3 ảnh cloud: `screenshots/dashboard.png`, `screenshots/running.png`, `screenshots/test.png`.
- [ ] Ảnh observability: `screenshots/grafana-dashboard.png`, `jaeger-slow-trace.png`, `jaeger-error-trace.png`, `prometheus-alert-firing.png`.
- [ ] Tra cứu/xác minh các trace ID trong Jaeger và lưu ảnh trace lỗi/chậm; log có ID đã lưu nhưng Jaeger chưa giữ trace khi stack dừng.
- [ ] Chạy riêng các thí nghiệm alert C/D/E; A và B chỉ chạy cùng nhau trong lượt chaos đã ghi, nên chưa có timing riêng.

Không đưa `.env`, key/token thật hoặc ảnh có thông tin bí mật vào bài nộp. Output hiện có là đối chiếu tham khảo; hãy đọc lại và đảm bảo hiểu nội dung trước khi nộp.
