from agent import create_research_assistant

def run():
    print("=== 🎓 Day 19: Đồ án Trợ lý Nghiên cứu AI (AI Research Assistant) ===")
    print("Hệ thống sẽ: 1. Tìm thông tin -> 2. Vào đọc web chi tiết -> 3. Viết báo cáo tóm tắt.\n")

    assistant = create_research_assistant()

    print("💡 Thử thách: 'Nghiên cứu về lịch sử hình thành của công ty OpenAI và viết báo cáo đầy đủ'")
    
    while True:
        topic = input("\n👤 Chủ đề bạn muốn tìm hiểu: ")
        if topic.lower() in ["exit", "quit"]:
            break
        
        print("\n🔎 Bắt đầu quy trình nghiên cứu chuyên sâu...")
        try:
            response = assistant.invoke(topic)
            print(f"\n✅ Hoàn thành: {response['output']}\n")
        except Exception as e:
            print(f"❌ Xảy ra lỗi: {e}")

if __name__ == "__main__":
    run()
