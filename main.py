# Creation Date: 12/14/2023

# Imports
import os
from pathlib import Path
import sys
import pytz
import calendar
from time import sleep
from random import randint
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Custom Print Import
from logger_formats import Log

# See selenium locally: http://localhost:4444/ui#/sessions

def setup(method: str = 'local'):
    ''' Returns: Browser session. '''
    options = webdriver.ChromeOptions()
    if method == 'production':
        browser = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=options
        )
    else:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(5)
    return browser

class EnvironmentError(Exception):
    pass

def get_secrets():
    ''' Returns: Username and password loaded from ENV. '''
    load_dotenv()
    try:
        user = os.environ['USER']
        password = os.environ['PASS']
    except KeyError as e:
        raise EnvironmentError(f'.env {e} not set')
    return user, password

def login(browser: webdriver.Chrome):
    ''' Purpose: Logs into Instagram via Selenium. '''
    username, password = get_secrets()
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
    return f'Dartmouth | BC\n{day1} > {day2}'

def get_current_bio(browser: webdriver.Chrome):
    ''' Returns: Current Instagram biography text. '''
    get_account_details(browser)
    biography_input = browser.find_element(By.CSS_SELECTOR, "textarea[id='pepBio']")
    return biography_input.get_attribute('value')

def calculate_end(session_days: int = 1, session_hours: int = 0, session_minutes: int = 0):
    ''' Returns: Session restart date. '''
    return datetime.now() + timedelta(days=session_days, hours=session_hours, minutes=session_minutes)

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
        Log.status(f'Updated text ({datetime.now()}): \n{new_text}')
    sleep(randint(1, 2))
    return new_text

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
    Log.status(f"Updated profile photo {str(os.path.split(path.split('.')[0])[1])} ({datetime.now()})")
    sleep(randint(5, 10))

def slideshow_profile_picture(browser: webdriver.Chrome, path: str, index: int):
    p = Path(path)
    for image in p.iterdir():
        file_name = os.path.basename(image)
        file = os.path.splitext(file_name)[0]
        if int(file) == index:
            # change image
            update_profile_picture(browser, str(image))
            break


if __name__ == '__main__':
    fail = 0
    slideshow_index = 0
    while fail <= 10:
        environment = sys.argv[1] if len(sys.argv) >= 2 else 'local'
        Log.info(f'Running as: {environment}')
        browser = setup(environment)
        try:
            login(browser)
            Log.status('Login success!')
            current_text = get_current_bio(browser)
            Log.info(f'Current text: \n{current_text}')
            end_time = calculate_end(0, 0, 2)
            Log.info(f'Session restarts: {end_time}')
            count = 0
            while True:
                curr_time = datetime.now()
                if curr_time > end_time:
                    current_text = update_bio(browser, current_text)
                    sleep(randint(5, 10))
                    slideshow_profile_picture(browser, "./imagesTest", slideshow_index)
                    Log.status('Session expired, restarting')
                    browser.quit()
                    slideshow_index += 1
                    break
                fail = 0
                sleep(30)
                count += 1

        except EnvironmentError:
            Log.alert('Set .env file!')
            break
        except KeyboardInterrupt:
            browser.quit()
            break
        except Exception as e:
            Log.error(str(e))
            Log.trace(e.__traceback__)
            Log.warn(f'Failed: #{fail}')
            browser.quit()
            fail += 1
            sleep(randint(720, 960))
    Log.alert('Process exiting...')
    sys.exit(0)
