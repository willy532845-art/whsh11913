import os
import json
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
# Google 搜尋功能
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
        return []

    results = []
    for item in data["items"]:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", "")
        })
    return results


# =========================================================
# LLM 決策階段：是否需要搜尋？
# =========================================================
def llm_decide(user_input):
    """讓 LLM 決定是否需要使用搜尋工具"""
    prompt = f"""
你是一個智慧型資訊代理。請根據以下問題判斷是否需要進行網路搜尋。
若能直接回答，請回傳：
{{"tool": "none"}}
若需要搜尋，請回傳：
{{"tool": "search", "query": "搜尋的關鍵字"}}

問題如下：
{user_input}

請僅輸出 JSON，沒有多餘說明。
"""
    response = model.generate_content(prompt)
    text = response.text.strip()

    try:
        decision = json.loads(text)
        if isinstance(decision, dict) and "tool" in decision:
            return decision
    except json.JSONDecodeError:
        # 無法解析時，預設為不搜尋
        pass

    return {"tool": "none"}


# =========================================================
# LLM 總結階段：整合搜尋結果
# =========================================================
def llm_summarize(user_input, search_results):
    """將搜尋結果整理成簡潔回答"""
    if not search_results:
        return "❌ 沒有找到相關的搜尋結果。"

    context = "\n\n".join(
        [f"【{r['title']}】\n{r['snippet']}\n({r['link']})" for r in search_results]
    )

    prompt = f"""
你是一個資訊整合助手。以下是使用者的問題與搜尋結果。
請根據搜尋內容，撰寫一個簡潔、清楚、可信且自然語氣的最終回答。

使用者問題：
{user_input}

搜尋結果：
{context}

請產生最終回答：
"""
    response = model.generate_content(prompt)
    return response.text.strip()


# =========================================================
# 主流程：整合代理邏輯
# =========================================================
def main():
    print("🤖 智慧代理機器人啟動！")
    print("輸入 'exit' 離開。\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() == "exit":
            print("👋 再見！")
            break

        # Step 1️⃣ 判斷是否需要搜尋
        decision = llm_decide(user_input)
        tool = decision.get("tool", "none")

        if tool == "search":
            query = decision.get("query", user_input)
            print(f"🔍 模型決定需要搜尋：{query}")
            search_results = google_search(query)

            # Step 2️⃣ 搜尋結果總結
            answer = llm_summarize(user_input, search_results)
            print(f"\n🤖 最終回答：\n{answer}\n")

        else:
            # Step 3️⃣ 直接回答
            response = model.generate_content(user_input)
            print(f"🤖 {response.text.strip()}\n")


if __name__ == "__main__":
    main()
