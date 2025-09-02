from instagrapi import Client
from pathlib import Path
import pytz
import calendar
from time import sleep
from random import randint
from datetime import datetime, timedelta
import os
from termcolor import colored


# https://github.com/subzeroid/instagrapi?tab=readme-ov-file

def calculate_end(session_days: int = 1, session_hours: int = 0, session_minutes: int = 0):
    ''' Returns: Session restart date. '''
    return datetime.now() + timedelta(days=session_days, hours=session_hours, minutes=session_minutes)

def get_bio():
    current_time = datetime.now(pytz.timezone('America/New_York'))
    day1 = calendar.day_name[current_time.weekday()]
    day2 = calendar.day_name[(current_time + timedelta(days=1)).weekday()]
    return {"biography": f'Dartmouth | BC\n{day1} > {day2}'}

def get_testing_bio(num):
    return {"biography": f'Updated {num} times!\nCheck back every 10 minutes'}

def number_of_img(path: str):
    p = Path(path)
    cnt = 0
    for image in p.iterdir():
        cnt += 1
    return cnt

def get_img_path(path: str, index: int):
    p = Path(path)
    for image in p.iterdir():
        file_name = os.path.basename(image)
        file = os.path.splitext(file_name)[0]
        if int(file) == index:
            # return image path
            return image

def begin_slideshow(api: Client, minutes: int):
    slideshow_index = 0
    fail = 0
    imgs = number_of_img("./images")
    days = minutes//1440
    hours = (minutes%1440)//60
    mins = (minutes%60)
    number = 1
    while fail <= 10:
        try:
            end_time = calculate_end(days, hours, mins)
            print(colored(end_time, "blue"))
            while True:
                curr_time = datetime.now()
                print(colored(curr_time, "green"))
                if curr_time > end_time:
                    sleep(randint(5, 10))
                    act = get_testing_bio(number) #get_bio()
                    number += 1
                    img = get_img_path("./images", slideshow_index)
                    cl.account_edit(**act)
                    cl.account_change_picture(img)
                    if slideshow_index >= (imgs-1):
                        slideshow_index = 0
                    else:
                        slideshow_index += 1
                    print(colored("Changed", "yellow"))
                    break
                fail = 0
                sleep(int((mins/4)*60))
        except:
            print(colored("Could not change account", "red"))
            fail += 1
            sleep(randint(720, 960))


if __name__ == '__main__':
    try:
        cl = Client()
        cl.login("justin.sapun", "redroom87")
        begin_slideshow(cl, 10)
    except:
        print(colored("Failed to login", "red"))
