import os
import time
import subprocess
import pyautogui

def run_as_admin(exe_path):
    """
    用系統管理員身分啟動 exe
    """
    subprocess.run([
        "powershell",
        "-Command",
        f'Start-Process "{exe_path}" -Verb RunAs'
    ])

def wait_and_click(image, timeout=100, confidence=0.20):
    print(f"正在尋找 {image} ...")
    start_time = time.time()

    while time.time() - start_time < timeout:

        try:
            location = pyautogui.locateCenterOnScreen(image, confidence=confidence)
        except Exception as e:
            print(f"圖片搜尋錯誤：{e}")
            location = None

        if location:
            print(f"找到 {image}，正在點擊...")
            pyautogui.click(location)
            time.sleep(1)
            return True
        else:
            print("NO")

        time.sleep(0.5)

    print(f"錯誤：{image} 未找到")
    return False



exe_path = r"C:\Program Files\HoYoPlay\games\Star Rail Games\StarRail.exe"

img_start = "star1.png"
img_enter = "star2.png"

if not os.path.exists(exe_path):
    print("路徑錯誤：找不到 StarRail.exe")
    exit()

print("正在以系統管理員身分啟動星穹鐵道...")
run_as_admin(exe_path)

print("等待啟動器載入中...")
time.sleep(6)

wait_and_click(img_start)

print("等待遊戲進入主畫面中...")
time.sleep(6)

wait_and_click(img_enter)

print("所有自動操作完成！")