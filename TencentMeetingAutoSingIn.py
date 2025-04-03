import pyautogui
import pytesseract
import time
import cv2
import numpy as np
import pygetwindow as gw

# 配置参数
windows = gw.getWindowsWithTitle('')
if windows:
    print("Window Captured")
    windows[0].activate()
CHECKIN_BUTTON_IMAGE = 'img./intro.png'  # 提前截图的签到按钮图片
CHECK_IN = 'img./button.png'
POLLING_INTERVAL = 5  # 检测间隔（秒）
LOADING_TIME = 5  # 加载界面时间
TIMEOUT = 60 * 60 * 10  # 超时时间（秒）


def screen_capture(region=None):
    """ 截取屏幕区域（默认全屏） """
    screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def find_button(image_path, confidence=0.7):
    """ 在屏幕上查找匹配的按钮图像 """
    try:
        position = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        return position
    except Exception as e:
        print(f"图像识别错误: {e}")
        return None


def get_all_buttons(image_path, confidence=0.7):
    """ 获取屏幕上所有匹配的按钮坐标（按从上到下排序） """
    try:
        buttons = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        # 按Y轴坐标排序（优先点击屏幕上方的按钮）
        buttons_sorted = sorted(buttons, key=lambda b: b.top)
        return [(b.left + b.width // 2, b.top + b.height // 2) for b in buttons_sorted]
    except:
        return []


def delete_rep_point(lst, threshold=50):
    if not lst:
        return []

    to_remove = set()  # 存储需要删除的点的索引
    n = len(lst)

    for i in range(n):
        if i in to_remove:  # 如果已经标记删除，跳过
            continue
        x1, y1 = lst[i]
        for j in range(i + 1, n):
            if j in to_remove:  # 如果已经标记删除，跳过
                continue
            x2, y2 = lst[j]
            dx = x1 - x2
            dy = y1 - y2
            distance_sq = dx ** 2 + dy ** 2  # 平方距离，避免开方计算
            if distance_sq <= threshold ** 2:  # 如果距离 ≤ 阈值，标记删除
                to_remove.add(j)

    # 构造新列表，跳过被标记删除的点
    result = [point for idx, point in enumerate(lst) if idx not in to_remove]
    return result


def auto_checkin():
    start_time = time.time()
    print("开始检测签到按钮...")

    while time.time() - start_time < TIMEOUT:
        # 查找按钮
        buttons = get_all_buttons(CHECKIN_BUTTON_IMAGE)
        if not buttons:
            print("当前未检测到候选按钮")
            time.sleep(POLLING_INTERVAL)
            continue

        # 遍历所有按钮尝试点击
        attempt_count = 0
        buttons = delete_rep_point(buttons)
        for idx, (x, y) in enumerate(buttons):

            attempt_count += 1
            print(f"尝试第 {attempt_count} 次点击：坐标 ({x}, {y})")

            pyautogui.click(x, y)
            time.sleep(LOADING_TIME)

            # check_pos = find_text_on_screen(TARGET_TEXT)
            check_pos = find_button(CHECK_IN)
            if check_pos:
                x, y = check_pos
                print(f"找到坐标 ({x}, {y})")
                pyautogui.click(check_pos)
                print("签到一次！")
                # return True

        # 等待下一次检测
        time.sleep(POLLING_INTERVAL)

    print("超时，未找到签到按钮。")
    return False


if __name__ == "__main__":
    auto_checkin()
