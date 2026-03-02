import csv
import os
import time
from datetime import datetime
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox

# 防重複觸發秒數：同一 UID 在此秒數內再次讀到會被忽略，這裡是兩秒。
COOLDOWN_SEC = 2.0
#函式作用:UID的去除雜字元
def normalize_uid(raw: str) -> str:
    s = raw.strip().upper()
    s = s.replace("-", "").replace(" ", "")
    # UID 正規化：去除空白/連字號並轉大寫，統一比對格式。
    return s

class App:
    def __init__(self, root):
        self.root = root
        root.title("RFID 手機交付紀錄（HID）")

        # 名單設定（目前寫死在程式內，可改成讀 CSV）。
        # UID -> StudentID（座號/學號）
        self.uid_map = {
            "04A1B2C3D4": "12",
            "AABBCCDD11": "13",
        }
        # 全班名單（座號 01~40）
        self.class_list = [f"{i:02d}" for i in range(1, 41)]  # 01~40，可自行改

        # 今日日期（用於建立當日日誌檔）
        self.today = datetime.now().strftime("%Y-%m-%d")
        # 每節次交付紀錄：period -> {student_id: time_str}
        self.submitted_time = {p: {} for p in range(1, 9)}

        self.last_seen = {}  # uid -> last_seen_epoch，用於防連刷

        # UI：上方控制列（節次切換、清空本節、匯出總表）
        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="目前節次：").pack(side="left")
        self.period_var = tk.IntVar(value=1)
        self.period_box = ttk.Combobox(top, values=list(range(1, 9)), width=5, textvariable=self.period_var, state="readonly")
        self.period_box.pack(side="left", padx=5)

        ttk.Button(top, text="清空本節", command=self.clear_period).pack(side="left", padx=10)
        ttk.Button(top, text="匯出今日總表", command=self.export_daily_summary).pack(side="left")

        # UI：中間狀態列（顯示最後一次刷卡結果）
        mid = ttk.Frame(root, padding=10)
        mid.pack(fill="x")

        self.last_label = ttk.Label(mid, text="等待刷卡…", font=("Arial", 14))
        self.last_label.pack(anchor="w")

        # UI：下方雙欄（未交 / 已交）
        main = ttk.Frame(root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="本節：未交名單").pack(anchor="w")
        self.not_list = tk.Listbox(left, height=20)
        self.not_list.pack(fill="both", expand=True)

        ttk.Label(right, text="本節：已交名單（含時間）").pack(anchor="w")
        self.ok_list = tk.Listbox(right, height=20)
        self.ok_list.pack(fill="both", expand=True)

        self.refresh_lists()

        # 鍵盤事件：HID 字元先累積，遇 Enter 視為一筆 UID 完成。
        self.buffer = ""
        keyboard.on_press(self.on_key)

        # 日誌檔：若當日檔案不存在，先建立並寫入標頭。
        os.makedirs("logs", exist_ok=True)
        self.log_path = os.path.join("logs", f"{self.today}.csv")
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["date", "period", "uid", "student_id", "time", "result"])

    def clear_period(self):
        p = int(self.period_var.get())
        self.submitted_time[p] = {}
        self.refresh_lists()

    def refresh_lists(self):
        p = int(self.period_var.get())
        submitted = self.submitted_time[p]  # student_id -> time_str
        not_submitted = [sid for sid in self.class_list if sid not in submitted]

        self.not_list.delete(0, tk.END)
        for sid in not_submitted:
            self.not_list.insert(tk.END, sid)

        self.ok_list.delete(0, tk.END)
        for sid, tstr in sorted(submitted.items(), key=lambda x: x[0]):
            self.ok_list.insert(tk.END, f"{sid}  {tstr}")

    def write_log(self, period, uid, student_id, result, tstr):
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([self.today, period, uid, student_id, tstr, result])

    def handle_uid(self, raw_uid: str):
        uid = normalize_uid(raw_uid)
        if not uid:
            return

        now = time.time()
        last = self.last_seen.get(uid, 0)
        if now - last < COOLDOWN_SEC:
            # 防抖：同 UID 短時間重送直接忽略。
            return
        self.last_seen[uid] = now

        p = int(self.period_var.get())
        tstr = datetime.now().strftime("%H:%M:%S")

        student_id = self.uid_map.get(uid, "UNKNOWN")
        if student_id == "UNKNOWN":
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

    def export_daily_summary(self):
        # 匯出「座號 x 1~8 節」矩陣，空白欄位代表該節未交。
        out_path = os.path.join("logs", f"{self.today}_summary.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            header = ["student_id"] + [f"P{p}" for p in range(1, 9)]
            w.writerow(header)
            for sid in self.class_list:
                row = [sid]
                for p in range(1, 9):
                    row.append(self.submitted_time[p].get(sid, ""))  # 時間字串或空白
                w.writerow(row)
        messagebox.showinfo("匯出完成", f"已輸出：{out_path}")

    def on_key(self, e):
        # Enter 代表一筆 UID 結束，送進 handle_uid 處理。
        if e.name == "enter":
            raw = self.buffer
            self.buffer = ""
            self.handle_uid(raw)
            return
        # 只收單一可見字元，忽略 Shift/Ctrl 等特殊鍵。
        if len(e.name) == 1:
            self.buffer += e.name

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
