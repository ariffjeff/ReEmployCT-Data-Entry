import time

import colorama
from selenium.webdriver.common.by import By

from reemployct_data_entry import entry_weeklyCertification, entry_workSearch
from reemployct_data_entry.lib import webdriver as m_driver
from reemployct_data_entry.lib import wrangle_job_data as wrangle


def navigate(creds, jobData):
  
  site = "https://reemployct.dol.ct.gov/accessct/faces/login/login_local.xhtml"
  driver = m_driver.start_driver(site)

  ############
  # Login page
  ############

  input_username = m_driver.wait_find_element(driver, By.ID, 'userId')
  input_password = driver.find_element(by=By.ID, value='password')
  input_username.clear()
  input_password.clear()
  input_username.send_keys(creds.username)
  input_password.send_keys(creds.password)

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

  # navigate to weekly work search / certification
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
        m_driver.wait_for_page_by_screenID(driver, 'WC-800')
        break
      time.sleep(0.3) # give time between retries in case user is still moving mouse

  # detect Work Search Questionnaire page (site detects that work search job entries have not yet been finally submitted for the week)
  # if the work search job entries have already been submitted (as in user can't go back and edit them) then the website auto redirects to weekly certification
  print("Looking for screenID: WC-800")
  screenID = m_driver.wait_find_element(driver, By.ID, 'templateDivScreenId', forceDelay=0.3).text # force delay since text str doesn't load instantly
  print("Found screenID: {}".format(screenID))
  if(screenID == 'WC-800'): # Work Search Questionnaire page
    entry_workSearch.questionnaire(driver, CAPTCHA_TIMEOUT)

    job_data_wrangled = wrangle.sanitize(driver, jobData)
    jobData = job_data_wrangled['jobData']

    # error if user doesn't have enough unique jobs to match minimum compliance 
    if(len(jobData) < job_data_wrangled['entries_min'] - job_data_wrangled['entries_existing_n']):
      print(colorama.Fore.RED)
      print("Not enough jobs found in excel file to enter for target week!")
      print("{} jobs available to enter that aren't duplicates of any existing entries.".format(len(jobData)))
      print("You must enter at least {} more jobs into the excel file for the target week.".format(job_data_wrangled['entries_min'] - job_data_wrangled['entries_existing_n']) + colorama.Style.RESET_ALL)
      print(colorama.Fore.GREEN + "If you do not need to look at the existing entries, quit the browser." + colorama.Style.RESET_ALL)
      # quit when user closes browser
      try:
        # look for non existent element to hold page (exception raised when user closes browser)
        m_driver.wait_find_element(driver, By.ID, 'nothingnullnothingnullnothingnull', 60 * 60, silentPrint=True)
      except:
        return driver

    # enter job data
    jobRow_i = 0
    while(job_data_wrangled['entries_existing_n'] < job_data_wrangled['entries_min']):
      jobRow = jobData.iloc[jobRow_i]
      print(colorama.Fore.GREEN +
      "\n(Job: {}/{}) Entering data: {} - {}".format(job_data_wrangled['entries_existing_n'] + 1, job_data_wrangled['entries_min'], jobRow['Employer Name'], jobRow['Position Applied For'])
      + colorama.Style.RESET_ALL)
      if(job_data_wrangled['entries_existing_n'] > 0): # different page layout when existing entries are present
        m_driver.ScrollPage.BOTTOM(driver) # scroll to bottom of page to reveal button since many entries will push button out of view
        m_driver.wait_find_element(driver, By.ID, 'method__1', forceDelay=0.3).click() # Add Another Work Search
      entry_workSearch.enterWorkSearch(driver, jobRow)
      job_data_wrangled['entries_existing_n'] += 1
      jobRow_i += 1

    #####################
    # Work Search Summary
    #####################

    msg = 'Review all entries to ensure correctness, then click Submit.\nIf there are errors, either:\n1: Edit the entries and Submit or,\n2: Delete the bad entries, quit the browser, fix the excel data, and restart the program.'
    m_driver.msg_user_verify_entries(msg)

    #############################################################
    # Weekly Certification and Work Search Record Acknowledgement
    #############################################################

    m_driver.wait_find_element(driver, By.ID, 'esignature', timeout= -1, silentPrint=True, forceDelay=0.3).send_keys(creds.ssn_last4) # SSN last 4 digits
    driver.find_element(by=By.ID, value='method__2').click() # Next

    ######################################################
    # Please click the button to file weekly certification
    ######################################################

    # SUC-002 ("Your work search responses have been saved. Please click the button to file weekly certification")
    m_driver.wait_find_element(driver, By.ID, 'method').click() # File Weekly Certification
  else:
    print(colorama.Fore.YELLOW + "\nNo weeks are pending. (no active week to enter work search data for)\n" + colorama.Style.RESET_ALL)

  # check if SUC-002 page is loaded (weekly certification already submitted)
  print("Looking for ***NOT*** screenID: SUC-002")
  screenID = m_driver.wait_find_element(driver, By.ID, 'templateDivScreenId', forceDelay=0.3).text # force delay since text str doesn't load instantly
  print("Found screenID: {}".format(screenID))
  if(screenID != 'SUC-002'): # SUC-002 = No Weeks are pending for the entered SSN. (weekly cert entry not possible)
    entry_weeklyCertification.main(driver)

    m_driver.msg_user_verify_entries()

    # WC-301 will load if "Did you perform any work?" was set to "Yes"
    # WC-006 will load if it was set to "No"
    m_driver.wait_for_page_by_screenID(driver, 'WC-006') # Verify Weekly Certification Responses (previous page summary)
    m_driver.wait_find_element(driver, By.ID, 'method__2', silentPrint=True).click() # Next
    
    ######################################################################
    # Weekly Certification and Work Search Record Acknowledgement - WC-010
    ######################################################################

    m_driver.wait_find_element(driver, By.ID, 'esignature', forceDelay=0.3).send_keys(creds.ssn_last4) # SSN last 4 digits
    driver.find_element(by=By.ID, value='method__1').click() # Submit
  else:
    print(colorama.Fore.YELLOW + "\nNo weeks are pending. (no active week to enter weekly certification data for)\n" + colorama.Style.RESET_ALL)

  return driver
