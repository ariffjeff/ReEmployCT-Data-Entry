from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import modules_webdriver as m_driver
import usaddress
import stateDictionary as states

def questionnaire(driver, timeout=0):
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
  # WC-802 = no previous work entries present, WC-806 = one or more previous work entries present
  while(True):
    try:
      screenID = driver.find_element(By.ID, 'templateDivScreenId').text
      if(screenID == 'WC-802' or screenID == 'WC-806'):
        break
    except:
      break


def enterWorkSearch(driver, jobData_day):
  ############################
  # Work Search Record Details
  ############################
  
  # work search type dropdown - employer contact
  m_driver.wait_find_element(driver, By.ID, 'j_id_46_label', 120, forceDelay=0.3).click() # Type of Work Search - Dropdown
  driver.find_element(by=By.ID, value='j_id_46_1').click() # Type of Work Search - Employer Contact

  # Date of Work Search
  date = jobData_day['Date of Work Search']

  input_month = m_driver.wait_find_element(driver, By.ID, 'wsrDate_-month') # MM
  input_day = driver.find_element(by=By.ID, value='wsrDate_-day') # DD
  input_year = driver.find_element(by=By.ID, value='wsrDate_-year') # YYYY

  input_month.clear()
  input_day.clear()
  input_year.clear()

  input_month.send_keys(date.month)
  input_day.send_keys(date.day)
  input_year.send_keys(date.year)

  driver.find_element(by=By.ID, value='empName').send_keys(jobData_day['Employer Name']) # Employer Name

  # Get state name or its abbreviation from jobData_day['Employer Address'] - MUST BE US ADDRESS
  STATES_DICT = states.states()
  # create address dictionary
  address = jobData_day['Employer Address']
  address_parsed = usaddress.parse(address)
  address_dict = {}
  # rebuild similar address components into same dict elements since usaddress breaks them up by char block
  for div in range(0, len(address_parsed)):
    key = address_parsed[div][1]
    if(key not in address_dict):
      address_dict[key] = address_parsed[div][0]
    else:
      address_dict[key] += ' ' + address_parsed[div][0]
    if(address_dict[key][-1] == ','): # remove trailing commas
      address_dict[key] = address_dict[key][:-1]

  # convert state abbreviation to full state name
  state_name = address_dict['StateName']
  if(len(state_name) == 2):
    address_dict['StateName'] = STATES_DICT[state_name]

  # rebuild street address components into single value
  # US address components are sorted by standard, so loop through them to determine which dict elements to combine
  separater_key = 'StreetNamePostDirectional'
  address_line_1 = ''
  for key in usaddress.LABELS:
    if key in address_dict:
      address_line_1 += address_dict[key] + ' '
    if(key == separater_key):
      address_line_1 = address_line_1.rstrip()
      break


  driver.find_element(by=By.ID, value='address_-address1').send_keys(address_line_1) # Address Line 1
  driver.find_element(by=By.ID, value='address_-city').send_keys(address_dict['PlaceName']) # City

  driver.find_element(by=By.ID, value='address_-state_label').click() # State - Dropdown
  m_driver.wait_find_element(driver, By.XPATH, "//li[@data-label = '{}']".format(address_dict['StateName']), forceDelay=0.3).click() # State

  driver.find_element(by=By.ID, value='address_-zip').send_keys(address_dict['ZipCode']) # ZIP Code

  driver.find_element(by=By.ID, value='positionAppliedFor').send_keys(jobData_day['Position Applied For']) # Position Applied for
  driver.find_element(by=By.ID, value='methodOfCont_label').click() # Method Of Contact - Dropdown
  m_driver.wait_find_element(driver, By.ID, 'methodOfCont_4', forceDelay=0.3).click() # Method Of Contact - Online

  # shorten website to domain name and TLD
  website = jobData_day['Website Address']
  website = website.replace('https://', '').replace('http://', '').replace('www.', '') # the world's most sophisticated url shortener that actually works properly
  driver.find_element(by=By.ID, value='contWeb').send_keys(website) # If Online, Please enter Website Address (truncate to domain name + top level domain)

  driver.find_element(by=By.ID, value='resultFlag_label').click() # Result - Dropdown
  m_driver.wait_find_element(driver, By.ID, 'resultFlag_1', forceDelay=0.3).click() # Result - Application/Resume Filed But Not Hired

  driver.find_element(by=By.ID, value='method__3').click() # Next

# if __name__ == "__main__":
#   main(webdriver.Firefox(), )
