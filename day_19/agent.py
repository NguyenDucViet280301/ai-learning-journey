from langchain_ollama import ChatOllama
from tools import web_search, read_webpage, save_report
import re

class ResearchAgent:
    """Agent Nghiên cứu. Kết hợp Search và Đọc Web."""
    def __init__(self, model_name="llama3.2:3b"):  # Đã đổi sang model bạn vừa set
        self.llm = ChatOllama(
            model=model_name, 
            base_url="http://127.0.0.1:11434",
            temperature=0.3 # Cần chút sáng tạo để viết báo cáo hay hơn
        )
        self.tools = {
            "web_search": web_search,
            "read_webpage": read_webpage,
            "save_report": save_report
        }

    def _get_prompt(self, topic, scratchpad):
        return f"""ĐÓNG VAI LÀ: Trợ lý Nghiên cứu Khoa học. BẠN PHẢI CHỈ DÙNG TIẾNG VIỆT.
HƯỚNG DẪN TỪNG BƯỚC BẮT BUỘC MÀ BẠN PHẢI TUÂN THỦ:
- BƯỚC 1: Bắt đầu, sử dụng lệnh 'web_search' để tìm thông tin tổng quát và thu thập đường link (URL).
- BƯỚC 2: Ngay khi kết quả Tìm kiếm trả về một đường link URL, bạn LẬP TỨC sử dụng 'read_webpage' với thông số là đường link đó. KHÔNG ĐƯỢC phép 'web_search' liên tục.
- BƯỚC 3: Dựa trên bài đọc, tổng hợp báo cáo bằng tiếng Việt và dùng 'save_report' để lưu nó lại.

QUY TẮC CÚ PHÁP (Chỉ in ra đúng định dạng này 1 lần duy nhất mỗi nhịp):
Thought: [Suy nghĩ của bạn: Đang ở bước nào?]
Action: [chọn 1 từ: web_search, read_webpage, save_report]
Action Input: [Nội dung truyền. Nếu là read_webpage thì bắt buộc phải là 1 URL có chữ http...]

Khi báo cáo lưu thành công, hãy kết thúc bằng dòng: "Final Answer: Bài báo cáo đã được trích xuất hoàn thiện."

Chủ đề cần nghiên cứu: {topic}

{scratchpad}
Thought:"""

    def invoke(self, topic):
        scratchpad = ""
        # Nghiên cứu là một quá trình dài, tăng số vòng lặp
        for step in range(8):
            full_prompt = self._get_prompt(topic, scratchpad)
            
            print(f"\n--- [Bước {step+1}] AI Đang viết (Streaming) ---")
            content = ""
            
            # Sử dụng luồng (Stream) để chữ tự động nhả ra màn hình ngay khi AI nghĩ xong từ đó
            try:
                for chunk in self.llm.stream(full_prompt, stop=["Observation:", "\n(Wait"]):
                    text_chunk = chunk.content
                    print(text_chunk, end="", flush=True)
                    content += text_chunk
            except Exception as e:
                print(f"\n❌ Lỗi Model hoặc Ollama: {e}")
                return {"output": "Dừng khẩn cấp do lỗi kết nối với mô hình AI."}
                
            print("\n-----------------------------")

            if "Final Answer:" in content:
                final_output = content.split("Final Answer:")[1].strip()
                return {"output": final_output}

            action_match = re.search(r"Action:\s*(.*)", content)
            input_match = re.search(r"Action Input:\s*(.*)", content)
            
            if action_match and input_match:
                tool_name = action_match.group(1).strip()
                tool_input = input_match.group(1).strip()
                
                if tool_name in self.tools:
                    print(f"📖 [Agent Gọi: {tool_name} | Tham số: {tool_input}]")
                    observation = self.tools[tool_name].run(tool_input)
                    scratchpad += f"\n{content}\nObservation: {observation}\nThought:"
                else:
                    scratchpad += f"\n{content}\nObservation: Lệnh '{tool_name}' không tồn tại.\nThought:"
            else:
                scratchpad += f"\n{content}\nObservation: FORMAT ERROR. You must include 'Action: <tool>' and 'Action Input: <input>'.\nThought:"

        return {"output": "Giới hạn thời gian nghiên cứu đã hết."}

def create_research_assistant():
    return ResearchAgent()
