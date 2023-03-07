import colorama
from selenium import webdriver
from selenium.webdriver.common.by import By

from reemployct_data_entry.lib import webdriver as m_driver
from reemployct_data_entry.lib.job_control import PortalJobEntry


def questionnaire(driver: webdriver.Firefox, timeout=0) -> None:
  ###########################
  # Work Search Questionnaire
  ###########################

  # complete initial weekly certification questions
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[1]/td[4]/table/tbody/tr/td[1]/div/div[2]/span').click() # radio, Yes
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[4]/tbody/tr[5]/td/div/div/div/iframe').click() # captcha
  try:
    m_driver.wait_find_element(driver, By.ID, 'method__1', timeout, forceDelay=.2).click() # next
  except:
    m_driver.print_solveCaptcha(timeout)

  ############################
  # Work Search Record Details
  ############################

  # m_driver.waitGetElement(driver, By.ID, 'j_id_46_label', 240, forceDelay=.5) # wait for specific page
  # screenID = m_driver.waitGetElement(driver, By.ID, 'templateDivScreenId', 240, forceDelay=.5).text # wait for specific page

  # force wait until on either work search page
  # WC-802 = Work Search Record Details (the entry form) (auto loaded first if no previous work entries present), WC-806 = Work Search Summary (one or more previous work entries present)
  m_driver.wait_for_any_page_by_screenID(driver, ['WC-802', 'WC-806'])


def enterWorkSearch(driver: webdriver.Firefox, entry: PortalJobEntry) -> None:
  ############################
  # Work Search Record Details
  ############################

  # work search type dropdown - employer contact
  m_driver.wait_find_element(driver, By.ID, 'j_id_46_label', 120, forceDelay=0.3).click() # Type of Work Search - Dropdown
  driver.find_element(by=By.ID, value='j_id_46_1').click() # Type of Work Search - Employer Contact
  
  # Date of Work Search
  input_month = m_driver.wait_find_element(driver, By.ID, 'wsrDate_-month') # MM
  input_day = driver.find_element(by=By.ID, value='wsrDate_-day') # DD
  input_year = driver.find_element(by=By.ID, value='wsrDate_-year') # YYYY

  input_month.clear()
  input_day.clear()
  input_year.clear()

  input_month.send_keys(entry.date_of_work_search.month)
  input_day.send_keys(entry.date_of_work_search.day)
  input_year.send_keys(entry.date_of_work_search.year)

  driver.find_element(by=By.ID, value='empName').send_keys(entry.employer_name) # Employer Name

  driver.find_element(by=By.ID, value='address_-address1').send_keys(entry.employer_address.address_line_1) # Address Line 1
  driver.find_element(by=By.ID, value='address_-city').send_keys(entry.employer_address.city) # City

  driver.find_element(by=By.ID, value='address_-state_label').click() # State - Dropdown
  m_driver.wait_find_element(driver, By.XPATH, f"//li[@data-label = '{entry.employer_address.full_state_name()}']", forceDelay=0.3).click() # State

  driver.find_element(by=By.ID, value='address_-zip').send_keys(entry.employer_address.zip) # ZIP Code

  driver.find_element(by=By.ID, value='positionAppliedFor').send_keys(entry.position_applied_for) # Position Applied for
  driver.find_element(by=By.ID, value='methodOfCont_label').click() # Method Of Contact - Dropdown
  m_driver.wait_find_element(driver, By.ID, 'methodOfCont_4', forceDelay=0.3).click() # Method Of Contact - Online

  # shorten website to domain name and TLD
  website = entry.website_address
  website = website.replace('https://', '').replace('http://', '').replace('www.', '') # the world's most sophisticated url shortener that actually works properly
  driver.find_element(by=By.ID, value='contWeb').send_keys(website) # If Online, Please enter Website Address (truncate to domain name + top level domain)

  driver.find_element(by=By.ID, value='resultFlag_label').click() # Result - Dropdown
  m_driver.wait_find_element(driver, By.ID, 'resultFlag_1', forceDelay=0.3).click() # Result - Application/Resume Filed But Not Hired

  driver.find_element(by=By.ID, value='method__3').click() # Next

  # check if still on entry page (probably b/c data entry error) since clicking Next was denied by site
  print("Looking for screenID: WC-802")
  screenID = m_driver.wait_find_element(driver, By.ID, 'templateDivScreenId', forceDelay=0.4).text
  print("Found screenID: {}".format(screenID))
  if(screenID == 'WC-802'): # WC-802 = Work Search Record Details
    print(colorama.Fore.RED + "\nFailed to create Work Search entry!\nFix any errors on the page (as well as in the excel job file), then click Next." + colorama.Style.RESET_ALL)
    m_driver.wait_for_page_by_screenID(driver, 'WC-806') # Wait for Work Search Summary page


# if __name__ == "__main__":
#   main(webdriver.Firefox(), )
