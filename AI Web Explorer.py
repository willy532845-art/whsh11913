import os
import google.generativeai as genai
from dotenv import load_dotenv

def setup_gemini():
    """載入 API 金鑰並設定 Gemini 模型"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("❌ 找不到 GEMINI_API_KEY，請在 .env 檔案中設定")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-pro")

def chat(model):
    """主要對話流程"""
    print("🤖 Gemini 聊天機器人啟動（輸入 exit 結束）\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("👋 再見！")
            break

        try:
            response = model.generate_content(user_input)
            print(f"Gemini：{response.text.strip()}\n")
        except Exception as e:
            print(f"⚠️ 發生錯誤：{e}\n")

def main():
    model = setup_gemini()
    chat(model)

if __name__ == "__main__":
    main()

