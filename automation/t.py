import pyautogui
import time 
from AppOpener import open
import sys

totalAdded = 0
totalTry = 0

def followOne(pic,second=5,bMove = False):
    global totalAdded,totalTry
    time.sleep(second) 
    try:
        button7location = pyautogui.locateOnScreen(pic, confidence=0.8)
        print('image found')
        button7point = pyautogui.center(button7location)
        print("Clicked  ",totalAdded, button7point)
        button7x, button7y = button7point
        pyautogui.click(button7x, button7y)  # clicks the center of where the 7 button was found
        pyautogui.moveTo(button7x+120, button7y+20, duration=0)
        totalAdded =totalAdded+1
    except pyautogui.ImageNotFoundException:
        print('ImageNotFoundException: image not found')
        pyautogui.scroll(-1000)
        #pyautogui.hotkey('F5')  # ctrl-c to copy

   
def getScreen():
    im1 = pyautogui.screenshot()
    im2 = pyautogui.screenshot('my_screenshot.png')
    time.sleep(10) 


def followAll():
    try:
         for pos in pyautogui.locateAllOnScreen('follow.png',  grayscale=False):
            print(pos)
    except pyautogui.ImageNotFoundException:
        print('ImageNotFoundException: image not found')

#time.sleep(10)
#pyautogui.scroll(-1000)

#https://x.com/elonmask/followers
def autoTwitter():
    print("Auto")
    followOne("gray.png")
    time.sleep(2)
    pyautogui.write('https://x.com/elonmask/followers')
    #https://x.com/elonmusk/followers_you_follow
    pyautogui.hotkey('Enter')

    #open("google chrome") # Opens whatsapp
    #open("whatsapp, telegram") # Opens whatsapp & telegram

if __name__ == '__main__':
    
    args = sys.argv[1:]
    print(args)
    totalAdded = 0
    totalTry = 0

    while totalTry<int(args[1]):
        if args[0] =='news':
            followOne("news.png",3,True)
            totalTry = totalTry+ 2
        elif args[0] == 'trump':
            followOne('trump.png',3)
            totalTry =totalTry+ 1
        elif args[0] == 'rong':          
            followOne("follow.png",2,True)
            totalTry =totalTry+ 1
            followOne("unfollow.png",2,True)
        elif args[0] == 'weibo':
            followOne("weibo.png",12,True)
            totalTry =totalTry+ 1
        elif args[0] == 'tt':
            followOne("tt.png",2,True)
            totalTry =totalTry+ 1
        elif args[0] == 'facebook':
            followOne("facebook.png",2,True)
            totalTry =totalTry+ 1
        elif args[0] == 'inst':
            followOne("inst.png",3,True)
            totalTry =totalTry+ 1
        elif args[0] == 'link':
            followOne("linkedin.png",3,True)
            totalTry =totalTry+ 1
        else:
            print("3")
            autoTwitter()
    #print(f'Ontario tax for an income of ${income} is: ${ontario_tax:.2f}')
    pyautogui.alert(text=f'Done add ${totalAdded} followers by$ {totalTry}', title='Done', button='OK')

    #https://x.com/A_SHEKH0VTS0V/followers
    #This PC\Rong's S24+\内部存储\Android\data\com.tencent.mm\cache


    #https://www.youtube.com/watch?v=v1YOMrjcv04?sub_confirmation=1
    #https://www.youtube.com/shorts/Qm2rX8A5Z1w?sub_confirmation=1