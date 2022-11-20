import pandas as pd
import colorama
from selenium.webdriver.common.by import By
import modules_webdriver as m_driver

def main(driver, jobData):
  '''
  Sanitize and simplify user's excel job data.
  Only return job data that is required for satisfying ReEmployCT's work-search job entry requirements.
  '''

  # identify the number of existing job entries (this would implicitly reduce the number of entries needed to enter)
  entries_existing_n = 0
  entries_existing = []
  entries_min = 3 # minimum 3 work search entries for compliance
  if(driver.title == 'Work Search Summary'): # this page will appear instead of 'Work Search Record Details' if there are already existing entries
    entries_container = m_driver.wait_find_element(driver, By.XPATH, '/html/body/div[2]/div[5]/form/table[3]/tbody')
    entries_existing_scraped = entries_container.find_elements(By.XPATH, "./tr")
    entries_existing_n = len(entries_existing_scraped)
    print(colorama.Fore.GREEN +
    '\n{} existing work entries found. Must enter {} more for DOL compliance.'.format(entries_existing_n, entries_min - entries_existing_n)
      + colorama.Style.RESET_ALL)

    # rebuild data from existing entries
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
  # i = 0
  # for entry in entries_existing:
  #   keys_mark = []
  #   for key in entry: # mark keys of empty values
  #     if(entry[key] == ''):
  #       keys_mark.append(key)
  #   for key in keys_mark: # delete key value pairs
  #     del entry[key]
  #   # entries_existing_keys[i] = list(entries_existing[0])
  #   # i += 1
    
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

  return {
    'jobData': jobData,
    'entries_existing': entries_existing,
    'entries_min': entries_min,
    'entries_existing_n': entries_existing_n,
  }
