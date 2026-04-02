from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
import requests
from bs4 import BeautifulSoup
import os

# Sử dụng SearchResults thay vì SearchRun để AI nhìn thấy rõ đường link (URL)
search = DuckDuckGoSearchResults(num_results=3)

@tool
def web_search(query: str):
    """Tìm kiếm internet để tìm các nguồn bài viết, trang web. Trả về kết quả Tóm tắt kèm theo Link URL."""
    try:
        raw_result = search.run(query)
        # Lấy 800 ký tự đầu để bảo đảm chứa được các URL
        return raw_result[:800] + "...\n[Đã cắt bớt]" if len(raw_result) > 800 else raw_result
    except Exception as e:
        return f"Lỗi không thể tìm kiếm: {e}"

@tool
def read_webpage(url: str):
    """Đọc toàn bộ nội dung văn bản của một đường link URL cụ thể. (BẮT BUỘC nhận tham số chứa http:// hoặc https://)"""
    if "http" not in url:
        return "LỖI CÚ PHÁP: Tham số 'Action Input' cho read_webpage bắt buộc phải là một đường Link URL hợp lệ (bắt đầu bằng http...)"
    
    # Làm sạch URL nếu AI dính ngoặc hoặc dấu câu
    clean_url = url.strip("[]'\" ")
    # Thêm Header để tránh bị một số trang (như Wikipedia) chặn vì nghi ngờ bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(clean_url, headers=headers, timeout=10)
        response.encoding = 'utf-8' # Đảm bảo đọc đúng tiếng Việt
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy văn bản từ các thẻ p h1 h2 h3
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        
        if not text.strip():
            return "Cảnh báo: Không tìm thấy nội dung văn bản có ý nghĩa trên trang web này. Vui lòng thử một URL khác."

        # Lấy tối đa 1500 ký tự đầu tiên
        return text[:1500] + "...\n[Nội dung trang web đã dài quá mức cho phép]"
    except Exception as e:
        return f"Lỗi khi tải trang web: {str(e)}"

@tool
def save_report(content: str):
    """Lưu văn bản báo cáo nghiên cứu vào file markdown."""
    try:
        path = os.path.join(os.path.dirname(__file__), "research_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return "✅ Đã xuất báo cáo thành công ra file research_report.md"
    except Exception as e:
        return f"❌ Lỗi ghi file: {str(e)}"
