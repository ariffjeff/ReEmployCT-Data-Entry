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
import modules_webdriver as m_driver

def enterData(creds, jobData):
  
  USERNAME = creds.username
  PASSWORD = creds.password
  SSN_LAST4 = creds.ssn_last4

  print(colorama.Fore.RED + "\n*** AVOID MOVING YOUR MOUSE OVER THE WEB PAGE DURING ELEMENT NAVIGATION TO PREVENT UNEXPECTED BEHAVIOUR AND ERRORS ***\n" + colorama.Style.RESET_ALL)
  print("Starting web driver...")
  driver = webdriver.Firefox()
  site = "https://reemployct.dol.ct.gov/accessct/faces/login/login_local.xhtml"
  print("Loading: {}".format(site))
  driver.get(site)
  driver.maximize_window()

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
  ActionChains(driver).move_to_element(button_wc).perform() # move mouse to dropdown (user mouse movement causes dropdown to disappear)
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[3]/div/div/div/ul/li[2]/ul/li[1]/a').click() # File Weekly Certification

  ###########################
  # Work Search Questionnaire
  ###########################

  # complete initial weekly certification questions
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[1]/td[4]/table/tbody/tr/td[1]/div/div[2]/span').click() # radio, Yes
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[5]/td/div/div/div/iframe').click() # captcha
  try:
    m_driver.wait_find_element(driver, By.ID, 'method__1', CAPTCHA_TIMEOUT, forceDelay=.2).click() # next
  except:
    m_driver.print_solveCaptcha(CAPTCHA_TIMEOUT)

  ############################
  # Work Search Record Details
  ############################

  # m_driver.waitGetElement(driver, By.ID, 'j_id_46_label', 240, forceDelay=.5) # wait for specific page
  # screenID = m_driver.waitGetElement(driver, By.ID, 'templateDivScreenId', 240, forceDelay=.5).text # wait for specific page

  # force wait until on either work search page
  # WC-802 = no previous work entries present, WC-806 = one or more previous work entries present
  while(True):
    try:
      screenID = driver.find_element(By.ID, 'templateDivScreenId').text
      if(screenID == 'WC-802' or screenID == 'WC-806'):
        break
    except:
      break
  
  entries_existing_n = 0
  entries_min = 3 # minimum 3 work search entries for compliance
  # reduce number of entries to do if there are already existing entries
  if(driver.title == 'Work Search Summary'): # this page will appear instead of 'Work Search Record Details' if there are already existing entries
    entries_container = m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[3]/tbody')
    entries_existing_scraped = entries_container.find_elements(By.XPATH, "./tr")
    entries_existing_n = len(entries_existing_scraped)
    print(colorama.Fore.GREEN +
    '\n{} existing work entries found. Must enter {} more for DOL compliance.'.format(entries_existing_n, entries_min - entries_existing_n)
     + colorama.Style.RESET_ALL)
  
  # rebuild data from existing entries
  entries_existing = []
  for entry in entries_existing_scraped:
    cols = entry.find_elements(By.XPATH, './child::*')
    date_raw = cols[0].text
    summary_raw = cols[2].text.split('\n')
    summary = {}
    summary['Date of Work Search'] = pd.to_datetime(date_raw, format='%m/%d/%Y')
    for i in summary_raw:
      i = i.split(':')
      summary[i[0]] = i[1]
    entries_existing.append(summary)

  # filter out any excel job data days that already have a matching existing entry on the Work Search Summary page
  # doesn't account for when excel job and existing entry are the same job application but some column data is different (i.e. user retroactively added an email to excel job)
  # this is done by comparing cleaned dictionaries
  # clean existing entry dicts of empty values
  # entries_existing_keys = [[] for i in range(len(entries_existing))]
  i = 0
  for entry in entries_existing:
    keys_mark = []
    for key in entry: # mark keys of empty values
      if(entry[key] == ''):
        keys_mark.append(key)
    for key in keys_mark: # delete key value pairs
      del entry[key]
    # entries_existing_keys[i] = list(entries_existing[0])
    # i += 1
    
  # clean excel jobs rows and convert them to dicts
  jobData_toCompare = []
  for jobRow in range(len(jobData)):
    jobRow = jobData.iloc[jobRow]
    jobRow = jobRow.dropna()
    date_timestamp_col = jobRow['Date of Work Search'] # save timestamp dtype because .strip() destroys it
    jobRow = jobRow.str.strip() # strip leading and trailing whitespaces
    jobRow['Date of Work Search'] = date_timestamp_col
    jobRow = jobRow.drop('index')
    jobRow = jobRow.to_dict()
    jobData_toCompare.append(jobRow)
  
  def deleteDictKeys(dictionary, keys):
    dict_copy = dict(dictionary) # non reference copy
    for key in dict_copy:
      if(key not in keys):
        del dictionary[key]
    return dictionary

  # most simple unique indentifying info of a job application
  JOB_DATA_TO_MATCH = [
    'Date of Work Search',
    'Employer Name',
    'Position Applied For'
  ]
  # isolate dict key values to only the most simple unqiue identifying info that needs to be compared
  for jobRow in jobData_toCompare:
    jobRow = deleteDictKeys(jobRow, JOB_DATA_TO_MATCH)
  for entry in entries_existing:
    entry = deleteDictKeys(entry, JOB_DATA_TO_MATCH)

  # filter out existing excel job data rows
  jobData_existing_indices = []
  for entry in entries_existing:
    for jobRow in range(len(jobData_toCompare)):
      if(entry == jobData_toCompare[jobRow]):
        jobData_existing_indices.append(jobRow)
        break
  jobData = jobData.drop(jobData_existing_indices).reset_index()

  # error if user doesn't have enough unique jobs to match minimum compliance 
  if(len(jobData) < entries_min - entries_existing_n):
    print(colorama.Fore.RED)
    print("Not enough jobs found in excel file to enter for target week!")
    print("{} jobs available to enter that aren't duplicates of any existing entries.".format(len(jobData)))
    print("You must enter at least {} more jobs into the excel file for the target week.".format(entries_min - entries_existing_n) + colorama.Style.RESET_ALL)
    print(colorama.Fore.GREEN + "If you do not need to look at the existing entries, quit the browser." + colorama.Style.RESET_ALL)
    # quit when user closes browser
    try:
       # look for non existent element to hold page (exception raised when user closes browser)
      m_driver.wait_find_element(driver, By.ID, 'nothingnullnothingnullnothingnull', 60 * 60, silentPrint=True)
    except:
      return driver

  # enter job data
  while(entries_existing_n < entries_min):
    jobRow = jobData.iloc[entries_existing_n]
    print(colorama.Fore.GREEN +
    "\n(Job: {}/{}) Entering data: {} - {}".format(entries_existing_n + 1, entries_min, jobRow['Employer Name'], jobRow['Position Applied For'])
    + colorama.Style.RESET_ALL)
    if(entries_existing_n > 0): # different page layout when existing entries are present
      driver.find_element(by=By.ID, value='method__1').click() # Add Another Work Search
    entry_workSearch.main(driver, jobRow)
    entries_existing_n += 1

  #####################
  # Work Search Summary
  #####################

  inputTimeout = 60 * 10
  print("\n" + colorama.Fore.GREEN
    + "**"*41
    + "\n"
    + "Review all entries to ensure correctness, then Submit. " + str(inputTimeout) + " seconds until timeout."
    + "\n"
    + "**"*41
    + colorama.Style.RESET_ALL + "\n")

  #############################################################
  # Weekly Certification and Work Search Record Acknowledgement
  #############################################################

  m_driver.wait_find_element(driver, By.ID, 'esignature', timeout=inputTimeout, silentPrint=True).send_keys(SSN_LAST4) # SSN last 4 digits
  driver.find_element(by=By.ID, value='method__2').click() # Next

  ######################################################
  # Please click the button to file weekly certification
  ######################################################

  m_driver.wait_find_element(driver, By.ID, 'method').click() # File Weekly Certification

  ##############################
  # Weekly Certification Details
  ##############################

  # Were you physically able to work full time?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[1]/td[5]/table/tbody/tr/td[1]/div/div[2]').click()
  # Were you available for full time work?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[4]/td[5]/table/tbody/tr/td[1]/div/div[2]').click()
  # Did you start school, college or training, which you have not already reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[6]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you work in any self-employment not previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[7]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you perform any work?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[8]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Do you have a definite date to return to full time employment?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[10]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you refuse any offer of work or rehire?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[12]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you receive your first payment from a pension, other than Social Security, that you have not already reported or was there a change in the amount previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[13]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you receive dismissal pay(such as severance pay, vacation pay,etc.) or workers compensation benefits, not previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/table[4]/tbody/tr[1]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()

  m_driver.wait_find_element(driver, By.ID, 'method__1').click() # Next

  #######################################
  # Verify Weekly Certification Responses
  #######################################

  m_driver.wait_find_element(driver, By.ID, 'method__2').click() # Next

  #############################################################
  # Weekly Certification and Work Search Record Acknowledgement
  #############################################################

  driver.find_element(by=By.ID, value='esignature') # SSN last 4 digits
  driver.find_element(by=By.ID, value='method__1').click() # Submit

  ###################################
  # Weekly Certification Confirmation
  ###################################

  return driver
