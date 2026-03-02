# ==============================================
# 超詳細註解版（逐行說明）
# 說明：
# 1) 本檔的「可執行程式碼」與 test.py 保持相同邏輯。
# 2) 只額外加入大量註解，協助你理解每個語法與每一步驟。
# 3) 若要實際執行，請用：python test_super_detailed_comments.py
# ==============================================

# 匯入 csv 模組：用來寫入逗號分隔檔案（CSV）
import csv
# 匯入 os 模組：處理路徑、資料夾建立、檔案是否存在等作業
import os
# 匯入 time 模組：取得 epoch 秒數，做防連續刷卡判斷
import time
# 從 datetime 模組匯入 datetime 類別：取得現在日期與時間字串
from datetime import datetime
# 匯入 keyboard 套件：監聽鍵盤按鍵事件（HID 讀卡器通常模擬鍵盤輸入）
import keyboard
# 匯入 tkinter 主命名空間並命名為 tk：建立 GUI 用
import tkinter as tk
# 從 tkinter 匯入 ttk（主題化元件）與 messagebox（彈窗）
from tkinter import ttk, messagebox

# 防重複觸發秒數：同一 UID 在此秒數內再次讀到會被忽略，這裡是兩秒。
# 這是一個「全域常數」，命名用全大寫代表不預期在程式中被改動。
COOLDOWN_SEC = 2.0

# 函式作用：UID 的去除雜字元（正規化）
# def 是函式定義語法；raw: str 表示參數型別提示為字串；-> str 表示回傳型別提示為字串。
def normalize_uid(raw: str) -> str:
    # raw.strip()：去除字串前後空白；upper()：全部轉大寫，避免大小寫造成比對失敗。
    s = raw.strip().upper()
    # replace("-", "")：移除連字號；replace(" ", "")：移除中間空白。
    s = s.replace("-", "").replace(" ", "")
    # UID 正規化：去除空白/連字號並轉大寫，統一比對格式。
    return s

# class 關鍵字用來定義類別；App 代表整個應用程式（資料 + UI + 事件處理）。
class App:
    # __init__ 是建構子：建立 App(root) 物件時會自動執行。
    # root 是 tkinter 主視窗物件。
    def __init__(self, root):
        # self 代表目前這個物件本身；把 root 存成屬性，後續方法可使用。
        self.root = root
        # 設定主視窗標題。
        root.title("RFID 手機交付紀錄（HID）")

        # 名單設定（目前寫死在程式內，可改成讀 CSV）。
        # uid_map 是字典 dict：key=UID、value=StudentID（座號/學號）。
        self.uid_map = {
            "04A1B2C3D4": "12",
            "AABBCCDD11": "13",
        }
        # 全班名單（座號 01~40）
        # 串列生成式 [f"{i:02d}" for i in range(1, 41)]：
        # range(1,41) 會產生 1~40；f"{i:02d}" 把數字補零成兩位字串（01, 02, ...）。
        self.class_list = [f"{i:02d}" for i in range(1, 41)]  # 01~40，可自行改

        # 今日日期（用於建立當日日誌檔）
        # datetime.now() 取現在時間；strftime("%Y-%m-%d") 轉成 2026-03-03 這種日期格式。
        self.today = datetime.now().strftime("%Y-%m-%d")
        # 每節次交付紀錄：period -> {student_id: time_str}
        # 外層 dict 的 key 是節次 1~8；value 是另一個 dict，記該節誰在什麼時間已交。
        self.submitted_time = {p: {} for p in range(1, 9)}

        # last_seen 用來記每個 uid 最後被看到的時間（epoch 秒），用於防連刷。
        self.last_seen = {}  # uid -> last_seen_epoch，用於防連刷

        # UI：上方控制列（節次切換、清空本節、匯出總表）
        # ttk.Frame(...) 建立容器；padding=10 表示內距。
        top = ttk.Frame(root, padding=10)
        # pack(fill="x") 代表此容器沿 x 方向（水平）撐滿。
        top.pack(fill="x")

        # 在 top 放一個標籤文字。
        ttk.Label(top, text="目前節次：").pack(side="left")
        # tk.IntVar 是 tkinter 的「可綁定整數變數」，給 Combobox 使用。
        self.period_var = tk.IntVar(value=1)
        # 建立下拉選單：值 1~8、寬度 5、綁定到 period_var、readonly 禁止手打。
        self.period_box = ttk.Combobox(top, values=list(range(1, 9)), width=5, textvariable=self.period_var, state="readonly")
        # 放在左側，左右外距 5。
        self.period_box.pack(side="left", padx=5)

        # 按鈕1：清空當前節次資料，callback 綁定 self.clear_period。
        ttk.Button(top, text="清空本節", command=self.clear_period).pack(side="left", padx=10)
        # 按鈕2：匯出今日摘要，callback 綁定 self.export_daily_summary。
        ttk.Button(top, text="匯出今日總表", command=self.export_daily_summary).pack(side="left")

        # UI：中間狀態列（顯示最後一次刷卡結果）
        mid = ttk.Frame(root, padding=10)
        mid.pack(fill="x")

        # last_label 用來顯示「等待刷卡 / 成功 / 重複 / Unknown」訊息。
        # font=("Arial", 14) 指字型與大小。
        self.last_label = ttk.Label(mid, text="等待刷卡…", font=("Arial", 14))
        # anchor="w" 代表靠左對齊（west）。
        self.last_label.pack(anchor="w")

        # UI：下方雙欄（未交 / 已交）
        main = ttk.Frame(root, padding=10)
        # fill="both" + expand=True：視窗放大時主區塊可一起延展。
        main.pack(fill="both", expand=True)

        # 左右兩個子容器
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        # 左欄：未交名單
        ttk.Label(left, text="本節：未交名單").pack(anchor="w")
        self.not_list = tk.Listbox(left, height=20)
        self.not_list.pack(fill="both", expand=True)

        # 右欄：已交名單（含時間）
        ttk.Label(right, text="本節：已交名單（含時間）").pack(anchor="w")
        self.ok_list = tk.Listbox(right, height=20)
        self.ok_list.pack(fill="both", expand=True)

        # 初始化時先把目前節次名單算出來顯示。
        self.refresh_lists()

        # 鍵盤事件：HID 字元先累積，遇 Enter 視為一筆 UID 完成。
        # buffer 暫存每次刷卡輸入的字元序列。
        self.buffer = ""
        # 註冊全域按鍵事件回呼，按任意鍵時觸發 self.on_key。
        keyboard.on_press(self.on_key)

        # 日誌檔：若當日檔案不存在，先建立並寫入標頭。
        os.makedirs("logs", exist_ok=True)
        # 組合路徑 logs/YYYY-MM-DD.csv
        self.log_path = os.path.join("logs", f"{self.today}.csv")
        # 若今日檔案不存在，建立新檔並寫入 CSV 標頭列。
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                # csv.writer(f) 建立 CSV 寫入器。
                w = csv.writer(f)
                # 欄位順序固定，供後續分析使用。
                w.writerow(["date", "period", "uid", "student_id", "time", "result"])

    # 清空目前節次已交資料。
    def clear_period(self):
        # 取目前下拉選單值；IntVar.get() 回傳整數，保險起見再 int() 一次。
        p = int(self.period_var.get())
        # 把該節次資料清空成空字典。
        self.submitted_time[p] = {}
        # 資料改變後同步刷新 UI。
        self.refresh_lists()

    # 重建兩個名單（未交/已交）並更新 Listbox。
    def refresh_lists(self):
        # 讀目前節次
        p = int(self.period_var.get())
        # 取該節已交資料（dict: student_id -> time_str）
        submitted = self.submitted_time[p]  # student_id -> time_str
        # 用串列生成式算出未交名單：在 class_list 裡但不在 submitted keys 裡。
        not_submitted = [sid for sid in self.class_list if sid not in submitted]

        # 先清空左側未交 Listbox（從索引 0 到 END）。
        self.not_list.delete(0, tk.END)
        # 逐筆插入未交座號。
        for sid in not_submitted:
            self.not_list.insert(tk.END, sid)

        # 先清空右側已交 Listbox。
        self.ok_list.delete(0, tk.END)
        # submitted.items() 會得到 (sid, time)；sorted 依 sid 由小到大排序。
        for sid, tstr in sorted(submitted.items(), key=lambda x: x[0]):
            # 顯示格式："座號  時間"
            self.ok_list.insert(tk.END, f"{sid}  {tstr}")

    # 將單筆結果追加到當日日誌 CSV。
    def write_log(self, period, uid, student_id, result, tstr):
        # 以附加模式 a 開檔，不會覆蓋舊資料；newline="" 是 CSV 建議設定。
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            # 欄位順序需與標頭一致。
            w.writerow([self.today, period, uid, student_id, tstr, result])

    # 核心流程：處理一筆原始 UID。
    def handle_uid(self, raw_uid: str):
        # 先做 UID 正規化。
        uid = normalize_uid(raw_uid)
        # 若正規化後是空字串（例如只輸入空白），直接忽略。
        if not uid:
            return

        # 取得現在 epoch 秒數（float）。
        now = time.time()
        # 查這張卡上次出現時間；若沒出現過，預設 0。
        last = self.last_seen.get(uid, 0)
        # 若兩次間隔小於 COOLDOWN_SEC，判定為防抖情境。
        if now - last < COOLDOWN_SEC:
            # 防抖：同 UID 短時間重送直接忽略。
            return
        # 更新這張卡最新出現時間。
        self.last_seen[uid] = now

        # 讀目前節次。
        p = int(self.period_var.get())
        # 產生當下時間字串 HH:MM:SS。
        tstr = datetime.now().strftime("%H:%M:%S")

        # 透過 uid_map 對照學生；找不到就回傳 "UNKNOWN"。
        student_id = self.uid_map.get(uid, "UNKNOWN")
        if student_id == "UNKNOWN":
            # Unknown 卡路徑：顯示訊息 + 記錄 log。
            result = "UNKNOWN"
            self.last_label.config(text=f"[{tstr}] Unknown UID: {uid}")
            self.write_log(p, uid, student_id, result, tstr)
            return

        # 同節次重複刷同一位學生，記錄為 DUPLICATE。
        if student_id in self.submitted_time[p]:
            result = "DUPLICATE"
            self.last_label.config(text=f"[{tstr}] 重複：{student_id} (UID {uid})")
            self.write_log(p, uid, student_id, result, tstr)
            return

        # 首次成功：寫入交付時間、更新日誌與畫面。
        self.submitted_time[p][student_id] = tstr
        result = "OK"
        self.last_label.config(text=f"[{tstr}] OK：{student_id} 已交")
        self.write_log(p, uid, student_id, result, tstr)
        self.refresh_lists()

    # 匯出「座號 x 節次」摘要表。
    def export_daily_summary(self):
        # 匯出「座號 x 1~8 節」矩陣，空白欄位代表該節未交。
        out_path = os.path.join("logs", f"{self.today}_summary.csv")
        # 以寫入模式 w 重新產出 summary 檔。
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            # 標頭：student_id + P1..P8
            header = ["student_id"] + [f"P{p}" for p in range(1, 9)]
            w.writerow(header)
            # 每位學生一列
            for sid in self.class_list:
                row = [sid]
                # 每節次補上時間或空字串
                for p in range(1, 9):
                    row.append(self.submitted_time[p].get(sid, ""))  # 時間字串或空白
                w.writerow(row)
        # 匯出完畢後顯示訊息框。
        messagebox.showinfo("匯出完成", f"已輸出：{out_path}")

    # 按鍵事件處理：將 HID 輸入拼成一筆 UID。
    def on_key(self, e):
        # Enter 代表一筆 UID 結束，送進 handle_uid 處理。
        if e.name == "enter":
            # 取出暫存字串
            raw = self.buffer
            # 清空 buffer 以準備下一筆
            self.buffer = ""
            # 把完整 UID 送去核心流程
            self.handle_uid(raw)
            return
        # 只收單一可見字元，忽略 Shift/Ctrl 等特殊鍵。
        if len(e.name) == 1:
            # 把字元接到 buffer 尾端
            self.buffer += e.name

# Python 主程式入口：只有直接執行本檔時才會進來。
if __name__ == "__main__":
    # 建立 Tk 主視窗
    root = tk.Tk()
    # 建立 App 物件（初始化 UI 與事件）
    app = App(root)
    # 啟動 GUI 事件迴圈（阻塞直到視窗關閉）
    root.mainloop()
