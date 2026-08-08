import cv2
import numpy as np
import subprocess
import os
import time
import pyautogui
#截图保存到手机上， 上传到电脑上
def screencap():
    execute_cmd('adb shell screencap -p /sdcard/screen.png')
    execute_cmd('adb pull /sdcard/screen.png')


#用来执行命令，这里加了延迟
def execute_cmd(args):
    DELAY_SECOND = 3#延迟时间， 因为网络和手机响应速度不同，反应慢的可以改大一些。
    time.sleep(DELAY_SECOND) #等待上一步操作响应完成
    os.system(args)

# Detect buttons in the screenshot
def detect_buttons():
    # Load the main image and the button template
    img_rgb = cv2.imread('screen.png')
    template = cv2.imread('button.png')

    # Convert to grayscale for template matching
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Get dimensions of the template
    w, h = template_gray.shape[::-1]

    # Perform template matching
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Set a threshold for matching confidence
    threshold = 0.8
    loc = np.where(res >= threshold)

    count = 0
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
        print(pt)
        if count%5 == 0:
            click(pt[0] + w//2, pt[1] + h//2)
            time.sleep(1)  # 等待上一步操作响应完成
        count += 1

 

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print(min_loc)
    return len(loc[0])

def click(x ,y):
   
    cmd = f"adb shell input tap {x} {y}"
    print("Clicking the button...",cmd)   
    DELAY_SECOND = 1#延迟时间， 因为网络和手机响应速度不同，反应慢的可以改大一些。    
    process = subprocess.Popen(cmd,shell=True)
    time.sleep(DELAY_SECOND) #等待上一步操作响应完成

def swipe(x1,y1,x2,y2):
    cmd = f"adb shell input swipe {x1} {y1} {x2} {y2} 100"
    print("Swiping the screen...",cmd)
    DELAY_SECOND = 2  # 延迟时间， 因为网络和手机响应速度不同，反应慢的可以改大一些。
    process = subprocess.Popen(cmd, shell=True)
    time.sleep(DELAY_SECOND)  # 等待上一步操作响应完成
    
if __name__ == '__main__':
    print("Starting the button detection script...")
    total_attempts = 0
    while total_attempts < 50:
        screencap()
        detect_buttons()
        total_attempts += 1
        swipe(500,1000,500,630)
        print(f"Attempt {total_attempts}: Clicked the button.")
    print(f"Total attempts made: {total_attempts}")
    print("Button detection script completed.")
    pyautogui.alert( text="done add funs", title='Done', button='OK')
