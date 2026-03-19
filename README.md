# Tiếng Việt / English
*For English, please scroll down.*

# 🛡️ Proxy IPv6 Generator

Proxy IPv6 Generator là một công cụ mã nguồn mở giúp bạn khởi tạo, quản lý và sử dụng Proxy IPv6 một cách dễ dàng và tự động trên hệ điều hành Windows. Công cụ sử dụng `3proxy` làm nhân kết nối và tự động gọi các lệnh hệ thống để gán IPv6 hàng loạt.

## ✨ Tính năng nổi bật
- **Tạo Proxy số lượng lớn**: Tự động sinh ngẫu nhiên IPv6 từ /64 và gán vào Network Interface.
- **Xoay IP (Rotate IP) linh hoạt**: Hỗ trợ xoay IP toàn bộ hoặc từng proxy lẻ chỉ với 1 click. Xoay tự động theo thời gian định sẵn.
- **Bảo mật**: Hỗ trợ chuẩn xác thực Username/Password hoặc chạy Public (cảnh báo bảo mật).
- **Quản lý kết nối**: Theo dõi trực tiếp số kết nối (connections) đang sống trên từng proxy.
- **Kiểm tra ngoại tuyến**: Check proxy Live/Dead siêu mượt nhờ thuật toán xử lý luồng (thread) tối ưu.
- **Đa ngôn ngữ**: Giao diện hỗ trợ cả Tiếng Việt và Tiếng Anh.

## 🚀 Cài đặt

1. Yêu cầu cài đặt **Python 3.8+**.
2. Clone repository này về máy:
   ```bash
   git clone https://github.com/hungzerommo/proxy-ipv6-generator.git
   cd proxy-ipv6-generator
   ```
3. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
4. Đảm bảo bạn đã có sẵn thư mục `3proxy` trong thư mục gốc của dự án.
5. Chạy tool:
   ```bash
   python main.py
   ```

## 🛠 Cấu trúc thư mục
- `core/`: Chứa mã nguồn tính toán, tạo proxy, check proxy, và quản lý ngôn ngữ.
- `ui/`: Các file quản lý giao diện đồ họa.
- `locales/`: Nơi chứa bộ từ điển đa ngôn ngữ (`vi.json`, `en.json`).

## 🙏 Nguồn tham khảo & Lời cảm ơn (Credits)
Dự án này sử dụng mã nguồn đóng gói của [3proxy](https://github.com/3proxy/3proxy) để điều hướng các kết nối. Mọi bản quyền về core Proxy engine thuộc về các lập trình viên của dự án 3proxy.

---

# 🛡️ Proxy IPv6 Generator (English)

An open-source tool that helps you easily and automatically generate, manage, and use IPv6 Proxies on Windows. It uses `3proxy` under the hood and systematically allocates IPv6 sequences to your network interface.

## ✨ Key Features
- **Mass Generation**: Randomly generates IPv6s from a /64 subnet and assigns them.
- **Flexible IP Rotation**: Supports rotating all IPs or single proxy IPs on the fly. Auto-rotates via a set timer.
- **Security**: Supports Proxy Authentication (Username/Password) or Public mapping.
- **Connection Monitor**: Live tracking of current active TCP connections per proxy.
- **Health Checker**: Multi-threaded seamless proxy Live/Dead checking without UI lag.
- **Multilingual**: UI dynamically translates between English and Vietnamese.

## 🚀 Installation & Usage

1. Install **Python 3.8+**.
2. Clone this repository:
   ```bash
   git clone https://github.com/hungzerommo/proxy-ipv6-generator.git
   cd proxy-ipv6-generator
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure the `3proxy` binary folder is placed in the root directory.
5. Run the application:
   ```bash
   python main.py
   ```

## 🙏 Acknowledgements / Credits
This tool relies on [3proxy](https://github.com/3proxy/3proxy) for its core proxy engine and low-level traffic routing. All rights and credits for the 3proxy engine go to the developers and maintainers of the 3proxy project.
