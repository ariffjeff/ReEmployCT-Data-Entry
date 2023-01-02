from datetime import timedelta

import colorama
import pandas as pd
import usaddress
from selenium.webdriver.common.by import By

from . import stateDictionary as states
from . import webdriver as m_driver


def sanitize(driver, jobData):
  '''
  Sanitize and simplify user's excel job data.
  Only return job data that is required for satisfying ReEmployCT's work-search job entry requirements.
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

def drop_bad_rows(df):
  '''
  Clean table - drop rows of bad types
  ''' 
  df['Date of Work Search'] = df['Date of Work Search'].apply(lambda x: pd.to_datetime(x, errors='coerce')) # sets bad values to None/NaN/NaT for easy parsing
  index_NaT = df.loc[pd.isna(df["Date of Work Search"]), :].index # get array of indices of rows where data is of None/NaN/NaT
  return df.drop(df.index[index_NaT]) # drop rows

def isolate_week_from_day(df, day_of_target_week):
  '''
  Isolate the rows of a week of job data from a pandas data frame based on a chosen day of a week
  Arguments:
    df : DataFrame obj
      A Pandas DataFrame that holds the job data
    day_of_target_week : Date obj
      A datetime date object that is set to any day of a desired week
    Returns dict of isolated DataFrame, start day, and end day for the target week
  '''
  # convert given date into SAT (0) - SUN (7) index format
  day_idx = (day_of_target_week.weekday() + 1) % 7 # get day's number: SUN = 0 ... SAT = 6
  day_start = pd.Timestamp(day_of_target_week - timedelta(day_idx)) # sunday
  day_end = pd.Timestamp(day_start + timedelta(6)) # saturday

  # isolate week
  target_days = df['Date of Work Search'].between(day_start, day_end) # marks target days as True
  df = df.loc[target_days == True] # isolate target week rows
  df.reset_index(inplace=True)
  return {
    'table_jobs': df,
    'day_start': day_start,
    'day_end': day_end
  }

def target_week_has_job_data(target_week):
  '''
  check if there is any job data for target week
  '''
  if(len(target_week['table_jobs']) == 0):
      print(colorama.Fore.RED +
      "\n*** You have no days of job data to enter for the target week! ({} - {}) ***\nQuitting script.".format(target_week['day_start'].date(), target_week['day_end'].date())
      + colorama.Style.RESET_ALL)
      return False
  return True


### US ADDRESSES

def clean_usaddress_parse(address_parsed) -> dict:
  '''
  Create a cleaned up dict of the parsed result of the usaddress package.

  Arguments:
    parse : usaddress obj
      the result of usaddress.parse(some_address)
  '''
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
  return address_dict

def state_abbrev_to_full_name(state_name) -> str:
  '''
  Convert US state name abbreviation to full state name
  '''
  STATES_DICT = states.states()
  if(len(state_name) == 2):
    try:
      return STATES_DICT[state_name]
    except:
      raise Exception("Full state name conversion of state abbreviation could not be found.")
  return state_name

def build_address_from_cleaned_address_dict(address_dict) -> str:
  '''
  Rebuild street address components of the cleaned address dict from a usaddress package parse into a single string
  '''
  SEPARATER_KEY = 'StreetNamePostDirectional'
  address_line_1 = ''
  # US address components are sorted by a US standard, so loop through them to determine which dict elements to combine
  for key in usaddress.LABELS:
    if key in address_dict:
      address_line_1 += address_dict[key] + ' '
    if(key == SEPARATER_KEY):
      address_line_1 = address_line_1.rstrip()
      break
  return address_line_1
