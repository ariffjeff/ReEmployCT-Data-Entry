from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import json
import credentialsController as credCon
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
import time
import colorama

def is_job_data_filepath_valid(filepath):
    if(not os.path.isfile(filepath) or os.path.splitext(filepath)[-1] != ".xlsx"):
        print("No user job data file found.")
        return False
    print("Job data found at: " + filepath)
    return True

# get job data filepath Filepath from json
JOB_FILEPATH_JSON = "jobDataLocation.json"
with open(JOB_FILEPATH_JSON, 'r') as file:
    json_jobDataFilepath = json.load(file)

# validate job data filepath
updateJobFilepath = False
while(not is_job_data_filepath_valid(json_jobDataFilepath['filepath_jobData'])):
    json_jobDataFilepath['filepath_jobData'] = input(colorama.Fore.GREEN + "Enter the filepath (including file extension) to your job data excel file: " + colorama.Style.RESET_ALL)
    updateJobFilepath = True

# set json job data filepath in
if(updateJobFilepath):
    with open(JOB_FILEPATH_JSON, 'w') as file:
        # jobDataFilepath = json.load(file)
        json.dump(json_jobDataFilepath, file)
    

################################## MODULARIZE FILE PATH LOGIC ##################################
################################## MODULARIZE FILE PATH LOGIC ##################################
################################## MODULARIZE FILE PATH LOGIC ##################################
################################## MODULARIZE FILE PATH LOGIC ##################################
# load excel job data
table_jobs = pd.read_excel(json_jobDataFilepath['filepath_jobData'])
# ask user which week (sunday - saturday) they want to enter data for
# get row data from week
# loop through desired cells and input into relevant fields


def userSetCredentials():
    print(colorama.Fore.GREEN + "Enter your DOL ReEmployCT credentials (encrypted and stored locally)..." + colorama.Style.RESET_ALL)
    credCon.main()

# no credentials file
if(not os.path.exists('key.key')):
    userSetCredentials()

creds = credCon.Credentials()
creds.rebuild_cred_from_file('CredFile.ini')
# expired credentials
if(creds.are_creds_expired()):
    print("Your credentials expired on " + creds.expire_time()['formatted'])
    userSetCredentials()

# option = webdriver.FirefoxOptions()
# option.binary_location = r'C:/Program Files/Mozilla Firefox/firefox.exe'
# driverService = Service('C:/Python3/geckodriver.exe')
# driver = webdriver.Firefox(service=driverService, options=option)

# driverService = "C:/Python3/geckodriver.exe"
# driver = webdriver.Firefox(executable_path=driverService)

def waitGetElement(driver, byType, elementID, delay=20):
    try:
        start = time.time()
        print("Waiting for page to render " + byType + " element: " + elementID)
        element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((byType, elementID)))
        seconds = str(int(time.time() - start))
        print(byType + " element found after " + seconds + " seconds.")
        return element
    except TimeoutException:
        print("Not able to get page element because page loading took too much time or element doesn't exist!")

def print_solveCaptcha(timeout):
    print("\n" + colorama.Fore.GREEN
    + "**"*37
    + "\n"
    + "Solve the captcha and then go to the next page. " + str(timeout) + " seconds until timeout."
    + "\n"
    + "**"*37
    + colorama.Style.RESET_ALL + "\n")


driver = webdriver.Firefox()

site = "https://reemployct.dol.ct.gov/accessct/faces/login/login_local.xhtml"
driver.get(site)
driver.maximize_window()

#  login
input_username = driver.find_element(by=By.ID, value='userId')
input_password = driver.find_element(by=By.ID, value='password')
input_username.clear()
input_password.clear()
# input_username.send_keys(creds['username'])
# input_password.send_keys(creds['password'])
input_username.send_keys(creds.username)
input_password.send_keys(creds.get_decoded_password())

button_captcha = driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[3]/form/table/tbody/tr/td/table/tbody/tr/td[3]/table/tbody/tr[6]/td/table/tbody/tr/td/div/div/div/iframe')
button_captcha.click()
CAPTCHA_TIMEOUT = 240
print_solveCaptcha(CAPTCHA_TIMEOUT)

# input_username.send_keys(Keys.ENTER)

# navigate to weekly certifications
# try:
#     myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, button_wc)))
#     print("Page is ready!")
# except TimeoutException:
#     print("Loading took too much time!")

# driver.implicitly_wait(.6) # wait for page element to render

# navigate to weekly certification
# not able to use driver.get() here since site produces error
button_wc = waitGetElement(driver, By.XPATH, '/html/body/div[2]/div[3]/div/div/div/ul/li[2]/a', CAPTCHA_TIMEOUT) # weekly certification dropdown, long delay since captcha solved by user
ActionChains(driver).move_to_element(button_wc).perform() # move mouse to dropdown (user mouse movement causes dropdown to disappear)
waitGetElement(driver, By.XPATH, '/html/body/div[2]/div[3]/div/div/div/ul/li[2]/ul/li[1]/a').click() # File Weekly Certification

# complete initial weekly certification questions
waitGetElement(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[1]/td[4]/table/tbody/tr/td[1]/div/div[2]/span').click() # radio, Yes
waitGetElement(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[5]/td/div/div/div/iframe').click() # captcha
print_solveCaptcha(CAPTCHA_TIMEOUT)
# driver.find_element(by=By.ID, value='method__1').click() # next

# work search type dropdown - employer contact
# driver.implicitly_wait(.2) # wait for page element to render
waitGetElement(driver, By.ID, 'j_id_46_label', 120).click()
# driver.find_element(by=By.ID, value='j_id_46_label').click()
driver.find_element(by=By.ID, value='j_id_46_1').click()



print("nothing")
# driver.quit()
