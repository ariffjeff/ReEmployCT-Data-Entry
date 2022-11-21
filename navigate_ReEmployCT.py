from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import colorama
from datetime import datetime, timedelta
import pandas as pd
import entry_workSearch
import entry_weeklyCertification
import modules_webdriver as m_driver
import wrangle_job_data
import time

def navigate(creds, jobData):
  
  USERNAME = creds.username
  PASSWORD = creds.password
  SSN_LAST4 = creds.ssn_last4

  site = "https://reemployct.dol.ct.gov/accessct/faces/login/login_local.xhtml"
  driver = m_driver.start_driver(site)

  ############
  # Login page
  ############

  input_username = m_driver.wait_find_element(driver, By.ID, 'userId')
  input_password = driver.find_element(by=By.ID, value='password')
  input_username.clear()
  input_password.clear()
  input_username.send_keys(USERNAME)
  input_password.send_keys(PASSWORD)

  button_captcha = driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[3]/form/table/tbody/tr/td/table/tbody/tr/td[3]/table/tbody/tr[6]/td/table/tbody/tr/td/div/div/div/iframe')
  button_captcha.click()
  CAPTCHA_TIMEOUT = 240
  try:
    m_driver.wait_find_element(driver, By.ID, 'method', CAPTCHA_TIMEOUT, forceDelay=.2).click() # Log In
  except:
    m_driver.print_solveCaptcha(CAPTCHA_TIMEOUT)

  ###########
  # Home Page
  ###########

  # navigate to weekly certification
  # not able to use driver.get() here since site produces error
  button_wc = m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[3]/div/div/div/ul/li[2]/a', CAPTCHA_TIMEOUT) # weekly certification dropdown, long delay since captcha solved by user
  attempt = 0
  attempt_max = 20
  while(attempt <= attempt_max):
    try:
      button_wc.click()
      m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[3]/div/div/div/ul/li[2]/ul/li[1]/a').click() # File Weekly Certification
      break
    except:
      attempt += 1
      if(attempt >= attempt_max):
        print(colorama.Fore.RED +
        "\nFailed to find and click on 'File Weekly Certification' button in the Weekly Certification dropdown.\nNavigate to the page manually."
        + colorama.Style.RESET_ALL)
        # WC-800 = Work Search Questionnaire
        m_driver.wait_for_page(driver, ['WC-800'])
        break
      time.sleep(0.3) # give time between retries in case user is still moving mouse

  # detect Work Search Questionnaire page (site detects that work search job entries have not yet been finally submitted for the week)
  # if the work search job entries have already been submitted (as in user can't go back and edit them) then the website auto redirects to weekly certification
  screenID = m_driver.wait_find_element(driver, By.ID, 'templateDivScreenId').text
  if(screenID != 'WC-800'):
    ##############################
    # Weekly Certification Details
    ##############################

    entry_weeklyCertification.main(driver)

    #############################################################
    # Weekly Certification and Work Search Record Acknowledgement
    #############################################################

    m_driver.wait_find_element(driver, By.ID, 'esignature').send_keys(creds.ssn_last4) # SSN last 4 digits
    driver.find_element(by=By.ID, value='method__1').click() # Submit

    return driver

  entry_workSearch.questionnaire(driver, CAPTCHA_TIMEOUT)

  wrangle = wrangle_job_data.main(driver, jobData)
  jobData = wrangle['jobData']

  # error if user doesn't have enough unique jobs to match minimum compliance 
  if(len(jobData) < wrangle['entries_min'] - wrangle['entries_existing_n']):
    print(colorama.Fore.RED)
    print("Not enough jobs found in excel file to enter for target week!")
    print("{} jobs available to enter that aren't duplicates of any existing entries.".format(len(jobData)))
    print("You must enter at least {} more jobs into the excel file for the target week.".format(wrangle['entries_min'] - wrangle['entries_existing_n']) + colorama.Style.RESET_ALL)
    print(colorama.Fore.GREEN + "If you do not need to look at the existing entries, quit the browser." + colorama.Style.RESET_ALL)
    # quit when user closes browser
    try:
      # look for non existent element to hold page (exception raised when user closes browser)
      m_driver.wait_find_element(driver, By.ID, 'nothingnullnothingnullnothingnull', 60 * 60, silentPrint=True)
    except:
      return driver

  # enter job data
  while(wrangle['entries_existing_n'] < wrangle['entries_min']):
    jobRow = jobData.iloc[wrangle['entries_existing_n']]
    print(colorama.Fore.GREEN +
    "\n(Job: {}/{}) Entering data: {} - {}".format(wrangle['entries_existing_n'] + 1, wrangle['entries_min'], jobRow['Employer Name'], jobRow['Position Applied For'])
    + colorama.Style.RESET_ALL)
    if(wrangle['entries_existing_n'] > 0): # different page layout when existing entries are present
      m_driver.ScrollPage.BOTTOM(driver) # scroll to bottom of page to reveal button since many entries will push button out of view
      m_driver.wait_find_element(driver, By.ID, 'method__1', forceDelay=0.3).click() # Add Another Work Search
    entry_workSearch.enterWorkSearch(driver, jobRow)
    wrangle['entries_existing_n'] += 1

  #####################
  # Work Search Summary
  #####################

  print("\n" + colorama.Fore.GREEN
    + "*"*89
    + "\n"
    + "Review all entries to ensure correctness, then click Submit.\nIf there are errors, either:\n1: Edit the entries and Submit or,\n2: Delete the bad entries, quit the browser, fix the excel data, and restart the program."
    + "\n"
    + "*"*89
    + colorama.Style.RESET_ALL + "\n")

  #############################################################
  # Weekly Certification and Work Search Record Acknowledgement
  #############################################################

  m_driver.wait_find_element(driver, By.ID, 'esignature', timeout= -1, silentPrint=True).send_keys(SSN_LAST4) # SSN last 4 digits
  driver.find_element(by=By.ID, value='method__2').click() # Next

  ######################################################
  # Please click the button to file weekly certification
  ######################################################

  m_driver.wait_find_element(driver, By.ID, 'method').click() # File Weekly Certification

  ###################################
  # Weekly Certification Confirmation
  ###################################

  return driver
