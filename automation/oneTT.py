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
    DELAY_SECOND = 1#延迟时间， 因为网络和手机响应速度不同，反应慢的可以改大一些。
    time.sleep(DELAY_SECOND) #等待上一步操作响应完成
    os.system(args)

# Detect buttons in the screenshot
def detect_buttons():
    # Load the main image and the button template
    img_rgb = cv2.imread('screen.png')
    template = cv2.imread('button1.png')

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

 

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print(min_loc)
    return len(loc[0])

def click():
    print("Clicking the button...")   
    DELAY_SECOND = 1#延迟时间， 因为网络和手机响应速度不同，反应慢的可以改大一些。    
    process = subprocess.Popen('adb shell input tap 994 1141',shell=True)
    time.sleep(DELAY_SECOND) #等待上一步操作响应完成
    swipe()

def swipe():
    print("Swiping the screen...")
  
    process = subprocess.Popen('adb shell input swipe 540 1300 540 500 100 ', shell=True)
    time.sleep(2)  # 等待上一步操作响应完成
    
if __name__ == '__main__':
    print("Starting the button detection script...")
    total_attempts = 0
    while total_attempts < 200:
        screencap()
        if detect_buttons() != 0:
            click()
            #swipe()
        else:
            print("No button detected, retrying...")
            swipe()
        total_attempts += 1
        print(f"Attempt {total_attempts}: Clicked the button.")
    print(f"Total attempts made: {total_attempts}")
    print("Button detection script completed.")
    #pyautogui.alert( text="done add funs", title='Done', button='OK')
