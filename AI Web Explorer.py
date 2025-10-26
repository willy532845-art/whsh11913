import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# =========================================================
# 初始化設定
# =========================================================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_SEARCH_CX")

if not all([GEMINI_API_KEY, GOOGLE_API_KEY, GOOGLE_CX]):
    raise ValueError("❌ 請確認 .env 檔案內已設定 GEMINI_API_KEY、GOOGLE_SEARCH_API_KEY、GOOGLE_SEARCH_CX")

# 設定 Gemini 模型
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")


# =========================================================
# 搜尋函式
# =========================================================
def google_search(query, num_results=5):
    """使用 Google Custom Search API 搜尋並回傳結果列表"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num_results
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if "items" not in data:
        print("⚠️ 沒有找到相關結果。")
        return []

    results = []
    for item in data["items"]:
        title = item.get("title", "無標題")
        link = item.get("link", "無連結")
        snippet = item.get("snippet", "")
        results.append({"title": title, "link": link, "snippet": snippet})

    return results


# =========================================================
# 主程式：可選擇「聊天」或「搜尋」
# =========================================================
def main():
    print("🤖 智慧機器人啟動！")
    print("輸入 'chat' 進入聊天模式，或輸入 'search' 進行網頁搜尋。")
    print("輸入 'exit' 離開。\n")

    while True:
        mode = input("選擇模式(chat/search/exit)：").strip().lower()

        if mode == "exit":
            print("👋 再見！")
            break

        elif mode == "chat":
            user_input = input("你：")
            response = model.generate_content(user_input)
            print(f"Gemini：{response.text.strip()}\n")

        elif mode == "search":
            query = input("🔍 搜尋關鍵字：").strip()
            results = google_search(query)
            print("\n📚 搜尋結果：\n")
            for i, r in enumerate(results, start=1):
                print(f"{i}. {r['title']}")
                print(f"   {r['link']}")
                print(f"   {r['snippet']}\n")

        else:
            print("⚠️ 無效的指令，請輸入 chat / search / exit。\n")


if __name__ == "__main__":
    main()
