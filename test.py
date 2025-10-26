import requests
import json
import os
import time  # 🔁 用於延遲與循環

# ---------- 基礎設定 ----------
API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"
ARCHIVE_FILE = "facts.json"


# ---------- 功能區 ----------
def load_archive(filename=ARCHIVE_FILE):
    """載入現有事實存檔，若不存在則回傳空清單"""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_archive(data, filename=ARCHIVE_FILE):
    """將事實清單儲存至本機"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_fact_from_api():
    """從 API 取得新事實"""
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("text", "").strip()
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def is_duplicate(fact, archive):
    """檢查事實是否重複"""
    return fact in archive


# ---------- 主邏輯 ----------
def main():
    """執行一次完整流程：載入、取得、檢查、儲存"""
    archive = load_archive()
    new_fact = get_fact_from_api()

    if not new_fact:
        print("⚠️ 無法取得新事實，請稍後再試。")
        return

    if is_duplicate(new_fact, archive):
        print("🟡 此事實已存在於存檔中，略過。")
    else:
        archive.append(new_fact)
        save_archive(archive)
        print("✅ 新事實已保存：")
        print(new_fact)


# ---------- 自動化執行區 ----------
if __name__ == "__main__":
    print("🚀 自動化事實收集器啟動中...\n")
    while True:
        print("--- Fetching new fact ---")
        main()  # 執行主要流程一次
        print("--- Waiting 60 seconds before next fetch ---\n")
        time.sleep(60)  # 延遲 60 秒後再次執行
