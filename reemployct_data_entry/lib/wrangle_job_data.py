import colorama
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

from . import webdriver as m_driver


def get_existing_entries(driver: webdriver.Firefox, silent=False) -> dict:
  '''
  Remove rows of job data that already exist as entries in ReEmployCT
  Should be executed on the work search page (where job data is entered) where there may be previous job entries present so they can be read.
  '''

  # identify the number of existing job entries (this would implicitly reduce the number of entries needed to enter)
  entries_existing_n = 0
  entries_existing = []
  entries_min = 3 # minimum 3 work search entries for compliance
  if(driver.title == 'Work Search Summary'): # this page will appear instead of 'Work Search Record Details' if there are already existing entries
    entries_container = m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[3]/tbody')
    entries_existing_scraped = entries_container.find_elements(By.XPATH, "./tr")
    entries_existing_n = len(entries_existing_scraped)

    if(not silent):
      if(entries_existing_n >= 3):
        print(colorama.Fore.GREEN +
        '\n{} existing work entries found. Minimum requirements already met.'.format(entries_existing_n)
          + colorama.Style.RESET_ALL)
      else:
        print(colorama.Fore.GREEN +
        '\n{} existing work entries found. Must enter {} more for DOL compliance.'.format(entries_existing_n, entries_min - entries_existing_n)
          + colorama.Style.RESET_ALL)

    # rebuild data from existing entries
    for entry in entries_existing_scraped:
      entries_existing.append(rebuild_entry(entry))
    del entries_existing_scraped

  return entries_existing


def rebuild_entry(entry) -> dict:
  '''
  Convert a job entry's raw data scrapped from page into a clean dict
  '''
  entry = entry.find_elements(By.XPATH, './child::*')
  date_raw = entry[0].text
  summary_raw = entry[2].text.split('\n')
  summary = {}
  summary['Date of Work Search'] = pd.to_datetime(date_raw, format='%m/%d/%Y')
  for i in summary_raw:
    i = i.split(':')
    summary[i[0]] = i[1]
  return summary
