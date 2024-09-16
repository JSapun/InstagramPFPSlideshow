import os
from pathlib import Path
import sys
import pytz
import calendar
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from termcolor import colored

def setup(method: str = 'windows'):
    ''' Returns: Browser session. '''
    chrome_options = webdriver.ChromeOptions()
    if method == 'pi':
        service = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(service=service, options=chrome_options)
    else:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.implicitly_wait(5)
    return browser

def login(browser: webdriver.Chrome, username : str, password : str):
    ''' Purpose: Logs into Instagram via Selenium. '''
    browser.get('https://www.instagram.com/')
    sleep(randint(5, 10))
    username_input = browser.find_element(By.CSS_SELECTOR, "input[name='username']")
    password_input = browser.find_element(By.CSS_SELECTOR, "input[name='password']")
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    sleep(randint(5, 10))

def get_account_details(browser: webdriver.Chrome):
    ''' Purpose: Loads the Instagram accounts page, verify one of CSS elements. '''

    browser.get('https://www.instagram.com/accounts/edit/')

    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[id='pepBio']")))

def build_text():
    ''' Returns: Built Instagram biography string. '''
    current_time = datetime.now(pytz.timezone('America/New_York'))
    day1 = calendar.day_name[current_time.weekday()]
    day2 = calendar.day_name[(current_time + timedelta(days=1)).weekday()]
    return f'Some School | Other School\n{day1} > {day2}'

def get_current_bio(browser: webdriver.Chrome):
    ''' Returns: Current Instagram biography text. '''
    get_account_details(browser)
    biography_input = browser.find_element(By.CSS_SELECTOR, "textarea[id='pepBio']")
    return biography_input.get_attribute('value')

def calculate_end(minutes: int = 10):
    ''' Returns: Session restart date. '''
    days = minutes // 1440
    hours = (minutes % 1440) // 60
    mins = (minutes % 60)
    return datetime.now() + timedelta(days=days, hours=hours, minutes=mins)

def verify_bio_update(browser: webdriver.Chrome):
    ''' Purpose: Catch exception if no browser indication of bio text update. '''
    try:
        WebDriverWait(browser, 8).until(EC.text_to_be_present_in_element(
            (By.XPATH, "//p[contains(text(), 'Profile saved.')]"), 'Profile saved.')
        )
    except TimeoutException:
        raise TimeoutException('Failed to verify that bio updated...')

def update_bio(browser: webdriver.Chrome, current_text: str):
    ''' Returns: Current bio - will update bio text if out of date. '''
    new_text = build_text()
    if current_text != new_text:
        get_account_details(browser)
        biography_input = browser.find_element(By.CSS_SELECTOR, "textarea[id='pepBio']")
        biography_input.clear()
        biography_input.send_keys(new_text)
        update_button = browser.find_element(By.XPATH, "//*[contains(text(), 'Submit')]")
        update_button.click()
        verify_bio_update(browser)
        print(colored("[-]", "white") + colored(f'Updated text ({datetime.now()}): \n{new_text}', "green"))
    sleep(randint(1, 2))

def verify_pfp_update(browser: webdriver.Chrome):
    ''' Purpose: Catch exception if no browser indication of bio text update. '''
    try:
        WebDriverWait(browser, 15).until(EC.text_to_be_present_in_element(
            (By.XPATH, "//p[contains(text(), 'Profile photo added.')]"), 'Profile photo added.')
        )

    except TimeoutException:
        raise TimeoutException('Failed to verify that profile photo updated...')

def update_profile_picture(browser: webdriver.Chrome, path: str):
    ''' Updates profile picture and verifies change. '''

    get_account_details(browser)
    image = os.path.abspath(path)  # need absolute path
    upload_maybe = browser.find_element(By.XPATH, "//input[@type='file' and @class='_ac69']")  # Secret form element
    upload_maybe.send_keys(image)  # upload

    ''' 
    Manual Sequence of button clicks to upload photo 
    Not required, can upload directly to secret form

    # click on "Change profile picture"
    change_button = browser.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl') and text()='Change profile photo']")
    change_button.click()
    sleep(randint(5, 10))

    # click on "Upload photo"
    upload_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Upload Photo')]")
    upload_button.send_keys(image)
    sleep(randint(5, 10))
    '''
    # Verify
    verify_pfp_update(browser)
    print(colored("[-]", "white") + colored(f"Updated profile photo {str(os.path.split(path.split('.')[0])[1])} ({datetime.now()})", "green"))
    sleep(randint(5, 10))

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

def begin_slideshow(user: str, pwd: str, minutes: int):
    fail = 0
    slideshow_index = 0
    imgs = number_of_img("./imagesTest")
    while fail <= 10:
        try:
            browser = setup()
            login(browser, user, pwd)
            print(colored("[-]", "white")+colored(' Login success!', "green"))
            current_text = get_current_bio(browser)
            print(colored("[i]", "white") + colored(f' Current text: \n{current_text}', "blue"))
            end_time = calculate_end(minutes)
            print(colored("[i]", "white")+colored(f' Session restarts: {end_time}', "blue"))
            while True:
                curr_time = datetime.now()
                if curr_time > end_time:
                    update_bio(browser, current_text)
                    sleep(randint(5, 10))
                    img = get_img_path("./imagesTest", slideshow_index)
                    update_profile_picture(browser, str(img))
                    print(colored("[i]", "white") + colored('Updated, session will restart', "blue"))
                    browser.quit()
                    if slideshow_index >= (imgs-1):
                        slideshow_index = 0
                    else:
                        slideshow_index += 1
                    browser.quit()
                    break
                fail = 0
                sleep(int((minutes/4)*60))

        except KeyboardInterrupt:
            #browser.quit()
            break
        except Exception as e:
            print(colored("[!]", "white") + colored(str(e), "red"))
            print(colored("[!]", "white") + colored(str(e.__traceback__), "red"))
            print(colored("[!]", "white") + colored(f'Failed: #{fail}', "red"))
            #browser.quit()
            fail += 1
            sleep(randint(720, 960))


if __name__ == '__main__':
    begin_slideshow("rnyannill", "rspamyan", 1)
    print(colored("[-]", "white") + colored('Process exiting...', "green"))
    sys.exit(0)
