# 🎓 Project: AI Research Assistant (Trợ lý Nghiên cứu Khoa học)

Chào mừng bạn đến với **Day 19**! Đây là dự án thực tế nhất trong lộ trình học tập Agent của chúng ta. Agent này không chỉ "nói suông" mà thực sự biết "đi làm việc" trên môi trường Internet.

---

## 🛠️ Cơ Chế Hoạt Động

Agent được thiết lập để thực hiện quy trình nghiên cứu 3 bước nghiêm ngặt:

1.  **Bước 1 - Khám phá (`web_search`)**: Sử dụng công cụ tìm kiếm DuckDuckGo để lấy danh sách các URL liên quan đến chủ đề.
2.  **Bước 2 - Thu thập kiến thức (`read_webpage`)**: Agent sẽ chọn một URL uy tín, truy cập vào trang web, sử dụng `BeautifulSoup4` để cạo (scrape) nội dung chữ và mang về để "đọc".
3.  **Bước 3 - Tổng hợp báo cáo (`save_report`)**: Sau khi đã có kiến thức từ web, Agent tự viết một bản tóm tắt khoa học bằng tiếng Việt và lưu xuống file Markdown.

---

## ✨ Điểm Cải Tiến Mới Nhất

- **Streaming Output**: Bạn có thể theo dõi quá trình AI "suy nghĩ" và "viết lách" trực tiếp trên Terminal theo thời gian thực.
- **Header Giả lập Trình duyệt**: Đã bổ sung User-Agent để Agent có thể vượt qua các lớp bảo vệ bot của Wikipedia và các báo lớn.
- **Vòng lặp Sửa lỗi (Fixing Loop)**: Nếu AI gọi sai cú pháp, hệ thống sẽ tự động nhắc nhở để AI tự sửa lại hành động của mình.

---

## ⚙️ Cài đặt & Chạy

1. **Cài đặt thư viện**:
   ```bash
   pip install requests beautifulsoup4 duckduckgo-search
   ```

2. **Khởi chạy**:
   ```bash
   python projects/day_19/main.py
   ```

3. **Mô hình kiến nghị**:
   Tốt nhất nên dùng `qwen2.5-coder:7b` hoặc `llama3.2:3b`.

---

## 📁 Cấu trúc Code
- `tools.py`: Các công cụ Search, Scrape và File IO.
- `agent.py`: Trái tim điều khiển luồng suy luận của Agent.
- `main.py`: Giao diện tương tác người dùng.
