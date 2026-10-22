# Hệ thống quản lý thư viện

Ứng dụng quản lý thư viện sử dụng FastAPI và PostgreSQL, triển khai bằng Docker Compose.

Hệ thống tích hợp Nginx làm reverse proxy, Prometheus và Grafana để giám sát, Loki và Promtail để tập trung nhật ký.

## 1. Công nghệ sử dụng

- FastAPI: xây dựng ứng dụng web và API.
- PostgreSQL: lưu trữ dữ liệu thư viện.
- pgAdmin: công cụ quản trị cơ sở dữ liệu PostgreSQL.
- Docker Compose: quản lý và triển khai các dịch vụ.
- Nginx: reverse proxy và security headers.
- Prometheus: thu thập metrics.
- Grafana: hiển thị dashboard và truy vấn log.
- Loki và Promtail: thu thập và tập trung nhật ký container.

## 2. Yêu cầu

- Docker Engine.
- Docker Compose plugin.
- Git.

## 3. Cấu hình môi trường

Tạo tệp môi trường từ tệp mẫu:

    cp .env.example .env

Chỉnh sửa tệp .env và đặt mật khẩu PostgreSQL mạnh trước khi triển khai.

Không đẩy tệp .env hoặc mật khẩu thật lên GitHub. Chỉ đưa .env.example chứa các giá trị mẫu lên repository.

## 4. Khởi chạy hệ thống

Tại thư mục dự án, chạy:

    docker compose up -d --build

Kiểm tra trạng thái các dịch vụ:

    docker compose ps

Xem nhật ký của Backend:

    docker compose logs -f backend

## 5. Truy cập hệ thống

- Website: http://127.0.0.1/
- pgAdmin: http://127.0.0.1:5050/
- Health check: http://127.0.0.1/health
- Prometheus: http://127.0.0.1:9090/
- Grafana: http://127.0.0.1:3000/
- Loki readiness: http://127.0.0.1:3100/ready

Các địa chỉ trên dựa theo cấu hình cổng trong compose.yaml.

## 6. Giám sát với Prometheus và Grafana

Prometheus thu thập metrics theo cấu hình tại prometheus/prometheus.yml.

Grafana hiển thị dashboard giám sát Backend, gồm trạng thái hoạt động, CPU và bộ nhớ.

## 7. Truy vấn log bằng LogQL

Trong Grafana, mở Explore và chọn nguồn dữ liệu Loki.

Truy vấn log Backend:

    {service="backend"}

Truy vấn log Nginx:

    {service="nginx"}

Lọc log Backend có nội dung GET:

    {service="backend"} |= "GET"

## 8. Biện pháp bảo mật

- Backend chạy bằng tài khoản không phải root.
- PostgreSQL sử dụng network nội bộ và không công khai cổng database ra máy host.
- Tệp .env được loại trừ khỏi Git.
- Nginx thiết lập các security headers.
- Các cổng dịch vụ giám sát được giới hạn truy cập theo cấu hình Docker Compose.

## 9. Dừng hệ thống

Chạy lệnh:

    docker compose down

Lệnh này dừng và xóa các container do Compose quản lý nhưng giữ lại dữ liệu trong named volumes. Không sử dụng docker compose down -v nếu muốn giữ dữ liệu.
