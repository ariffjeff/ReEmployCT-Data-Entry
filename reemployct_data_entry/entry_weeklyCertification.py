import colorama
from selenium.webdriver.common.by import By

from reemployct_data_entry.lib import webdriver as m_driver


def main(driver):
  #######################################
  # Weekly Certification Details - WC-004
  #######################################

  # Were you physically able to work full time?
  m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[1]/td[5]/table/tbody/tr/td[1]/div/div[2]').click()
  # Were you available for full time work?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[4]/td[5]/table/tbody/tr/td[1]/div/div[2]').click()
  # Did you start school, college or training, which you have not already reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[6]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you work in any self-employment not previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[7]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you perform any work?
  try:
    driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[8]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  except:
    print(colorama.Fore.YELLOW + "Skipping button since not able to click it. It might be disabled." + colorama.Style.RESET_ALL)
  # Do you have a definite date to return to full time employment?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[10]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you refuse any offer of work or rehire?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[12]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you receive your first payment from a pension, other than Social Security, that you have not already reported or was there a change in the amount previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/div[3]/table[1]/tbody/tr[13]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()
  # Did you receive dismissal pay(such as severance pay, vacation pay,etc.) or workers compensation benefits, not previously reported to the Labor Department?
  driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[5]/form/table[4]/tbody/tr[1]/td[5]/table/tbody/tr/td[2]/div/div[2]').click()

  # m_driver.wait_find_element(driver, By.ID, 'method__1').click() # Next

  #######################################
  # Verify Weekly Certification Responses
  #######################################

  # m_driver.wait_find_element(driver, By.ID, 'method__2').click() # Next
