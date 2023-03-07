import datetime

import colorama
import pandas as pd
import usaddress

from reemployct_data_entry.lib import stateDictionary
from reemployct_data_entry.lib import webdriver as m_driver
from reemployct_data_entry.lib.class_enum import ExtendedEnum
from reemployct_data_entry.lib.stateDictionary import States


class Jobs():

  '''
  A collection of all job entry data and metadata.
  Job data consists of three types:
    jobs_excel : excel job data read in as a raw pandas DataFrame
    jobs : modified and cleaned up version of jobs_excel that is convenient for high level use
    jobs_portal : the final stage of the job data that is formatted to match entry data for direct use in ReEmployCT
  '''

  def __init__(self, excel_path: str) -> None:
    self.jobs = pd.read_excel(excel_path) # the job data format for convenient high level use
    self.consistent_rows() 
    self.jobs_excel = self.jobs 
    self.jobs_portal = None
    self.required_num_of_portal_entries = 3

  def enough_entries_to_meet_minimum(self, existing: list) -> bool:
    '''
    Determine if there are enough new entries to enter into ReEmployCT to meet the minimum requirement.

    Arguments:
      existing : PortalJobEntries
    '''

    return len(self.jobs_portal.entries) < self.required_num_of_portal_entries - len(existing)

  def portal_format(self) -> None:
    '''
    Convert high level job data to ReEmployCT job entry formatted job data.
    '''

    self.jobs_portal = PortalJobEntries(self.jobs)
  
  def consistent_rows(self) -> None:
    '''
    Clean table - drop rows of bad data.
    This is mainly to get rid of rows that are completely different from all the others/that break
    dataframe consistency (e.g. a row with only a single populated cell of comment text).
    This is not meant to remove rows that contain NaNs.
    '''

    # set bad values to None/NaN/NaT for easy parsing
    self.jobs[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value] = self.jobs[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value].apply(lambda x: pd.to_datetime(x, errors='coerce'))
    index_NaT = self.jobs.loc[pd.isna(self.jobs[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value]), :].index # get array of indices of rows where data is of None/NaN/NaT
    self.jobs.drop(self.jobs.index[index_NaT]) # drop rows
  
  def target_week_has_jobs(self) -> bool:
    '''
    Check if there is any job data for target week.
    '''

    if(len(self.jobs) == 0):
        print(colorama.Fore.RED +
        f"\n*** You have no days of job data to enter for the target week! ({self.week.start.date()} - {self.week.end.date()}) ***\nQuitting script."
        + colorama.Style.RESET_ALL)
        return False
    return True
  
  def isolate_week(self, date_range) -> None:
    '''
    Set the start day and end day of the week (Sun through Sat) that contains the desired jobs.
    Isolate the desired jobs from those days.
    '''

    self.week = JobWeek(date_range)

    target_days = self.jobs[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value].between(self.week.start, self.week.end) # marks target days as True
    self.jobs = self.jobs.loc[target_days == True].reset_index() # isolate target week rows

  def sanitize(self) -> None:
    '''
    Drop rows from pandas dataframe of bad data such as NaNs (includes empty data).
    '''

    # clean excel jobs rows and convert them to dicts
    jobData_toCompare = []
    for i, jobRow in self.jobs.iterrows():
      jobRow.dropna(inplace=True)
      date_timestamp_col = jobRow[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value] # save timestamp dtype because .strip() destroys it
      jobRow = jobRow.str.strip() # strip leading and trailing whitespaces
      jobRow[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value] = date_timestamp_col
      jobRow = jobRow.drop('index')
      jobRow = jobRow.to_dict()
      jobData_toCompare.append(jobRow)

    self.jobs = pd.DataFrame(jobData_toCompare)
    self.jobs.dropna(inplace=True)
    self.jobs.reset_index(drop=True, inplace=True)

  def us_only_addresses(self) -> None:
    '''
    Remove rows from DataFrame that contain non US addresses in Employer Address
    '''

    states_full_names = States.value_list()
    states_full_names = [el.lower() for el in states_full_names]
    states_abbrev_names = States.key_list()
    states_abbrev_names = [el.lower() for el in states_abbrev_names]
    
    initial_n = len(self.jobs)
    indexes_to_drop = []
    for i, row in self.jobs.iterrows():
      address = Address.parse_us_address(row[Jobs_RequiredData.EMPLOYER_ADDRESS.value])
      address[Address_RequiredComponents.ADDRESS_LINE_1.value] = Address.build_street_address_from_cleaned_address_dict(address)

      try:
        # check for US state
        if(not(address[Address_RequiredComponents.STATE_NAME.value].lower() in states_abbrev_names or
               address[Address_RequiredComponents.STATE_NAME.value].lower() in states_full_names)):
          indexes_to_drop.append(i)
        else:
          # check all address components exist
          for comp in Address_RequiredComponents.value_list():
            if(len(address[comp]) == 0):
              indexes_to_drop.append(i)
              break
      except:
        # exception usually occurs when state name was never entered correctly/at all by user even if it was a US address
        # e.g. user enters US address like "1 W 1st St, New York, 10001, US" which is invalid because "New York" is only parsed as PlaceName here
        # it should instead be "1 W 1st St, New York, New York 10001, US"
        indexes_to_drop.append(i)

    addresses_to_drop = []
    for i in indexes_to_drop:
      addresses_to_drop.append(self.jobs.iloc[i][Jobs_RequiredData.EMPLOYER_ADDRESS.value])

    if(len(addresses_to_drop) > 0):
      m_driver.msg_user_verify_entries(f"{len(addresses_to_drop)} of {initial_n} job rows will be automatically excluded for the target week because they \
  contain invalid addresses and/or are non-U.S. addresses.\
  \nIf they are supposed to be U.S. addresses, please check they are entered correctly in your Excel data.\
  \nIf they are non-U.S. addresses, ReEmployCT won't accept them.", color="yellow")

      print(colorama.Fore.YELLOW, "Excluding jobs with these addresses...")
      for i in range(len(addresses_to_drop)):
        print(colorama.Fore.YELLOW, i + 1, ":", addresses_to_drop[i])

    self.jobs.drop(indexes_to_drop, inplace=True)

    remaining = initial_n - len(addresses_to_drop)
    if(remaining >= 1 and remaining < 3): # 0 remaining is dealt with later
      print(f"\nThere are only {remaining} valid entries remaining for the target week.\nThere may not be enough to enter to meet the minimum requirement of 3 entries.")

    print(colorama.Style.RESET_ALL)

  def isolate_columns(self, columns: list[str] | ExtendedEnum) -> None:
    '''
    Remove all but the desired columns from a DataFrame. Strings must match the names of columns in the data.
    '''

    if(type(columns) is not list):
      columns = [el.value for el in columns]

    self.jobs = self.jobs[columns]


class Jobs_RequiredData(ExtendedEnum):
    
    '''
    Required column data for a job application ("Employer Contact") in ReEmployCT
    '''
    
    DATE_OF_WORK_SEARCH = 'Date of Work Search'
    EMPLOYER_NAME = 'Employer Name'
    POSITION_APPLIED_FOR = 'Position Applied For'
    WEBSITE_ADDRESS = 'Website Address'
    EMPLOYER_ADDRESS = 'Employer Address'


class JobWeek():

  '''
  A standard calendar week (SUN-SAT) of a start and end day
  '''

  def __init__(self, date_range: datetime.datetime) -> None:
    # convert given date into SAT (0) - SUN (7) index format
    day_idx = (date_range.weekday() + 1) % 7 # get day's number: SUN = 0 ... SAT = 6
    self.start = pd.Timestamp(date_range - datetime.timedelta(day_idx)) # sunday
    self.end = pd.Timestamp(self.start + datetime.timedelta(6)) # saturday


class JobType(ExtendedEnum):

  '''
  Types of Work Searches listed in ReEmployCT
  '''

  EMPLOYER_CONTACT = 'Employer Contact'
  JOB_FAIR = 'Attending a job fair'
  INTERVIEW = 'Attending a Job Interview'
  WORKSHOP = 'Attending a work shop at an American Job Center'
  CREATED_USER_PROFILE = 'Creating a personal user profile on a professional networking site'
  CREATED_PLAN = 'Creating a Reemployment Plan'
  RESUME_TO_CTDOL = 'Creating and uploading resume to the CTDOL State Job Bank'
  REEMPLOYMENT_ACTIVITY = 'Participating in reemployment service activities at an American Job Center'


class PortalJobEntries():

  '''
  A collection of job entry data in ReEmployCT job entry format.
  Entries are dicts, all stored in a list.
  '''

  def __init__(self, jobs_high: pd.DataFrame | list[dict]) -> None:
    if((type(jobs_high)) is list):
      jobs_high = pd.DataFrame(jobs_high)

    entries = []
    for i, row in jobs_high.iterrows():
      entries.append(PortalJobEntry(JobType.EMPLOYER_CONTACT, row))
    self.entries = entries
    del entries
  
  def exclude_existing_entries(self, existing) -> None:
    '''
    Remove entries based on the existence of given duplicate entries.
    Duplicates entries are determined by specific values of each entry that are compared.
    '''

    if(len(existing.entries) == 0): return

    COMPARE = [
      Jobs_RequiredData.EMPLOYER_NAME.value_attrib(),
      Jobs_RequiredData.POSITION_APPLIED_FOR.value_attrib()
    ]

    entries_to_remove = []
    for e_main in self.entries:
      for e_existing in existing.entries:
        if(e_main.__getattribute__(COMPARE[0]) == e_existing.__getattribute__(COMPARE[0]) and 
           e_main.__getattribute__(COMPARE[1]) == e_existing.__getattribute__(COMPARE[1])):
          entries_to_remove.append(e_main)
          break

    for row in entries_to_remove:
      self.entries.remove(row)


class PortalJobEntry():

  '''
  A job entry that can be entered directly into ReEmployCT.
  '''

  def __init__(self, entry_type: JobType, entry: pd.Series) -> None:
    self.entry_type = entry_type.value

    # isolate only required column data for the given job type
    required_cols = Jobs_RequiredData.value_list()
    entry = entry[required_cols]

    # create job type framework
    self.create_entry_attribs(entry)

  def create_entry_attribs(self, entry: pd.Series) -> None:

    '''
    Create the required attribs for the given job entry.
    '''

    if(self.entry_type == JobType.EMPLOYER_CONTACT.value):
      self.date_of_work_search = entry[Jobs_RequiredData.DATE_OF_WORK_SEARCH.value]
      self.employer_name = entry[Jobs_RequiredData.EMPLOYER_NAME.value]
      self.employer_address = Address(entry[Jobs_RequiredData.EMPLOYER_ADDRESS.value])
      self.position_applied_for = entry[Jobs_RequiredData.POSITION_APPLIED_FOR.value]
      self.website_address = entry[Jobs_RequiredData.WEBSITE_ADDRESS.value]
      self.contact_method = ContactMethod.ONLINE.value
      self.result = ContactResult.FILED_BUT_NOT_HIRED.value


class ContactMethod(ExtendedEnum):

  '''
  Contact method Enums for a job entry
  '''

  NONE = None
  EMAIL = "Email"
  FAX = "Fax"
  IN_PERSON = "In Person"
  ONLINE = "Online"
  PHONE = "Telephone"


class ContactResult(ExtendedEnum):
  
  '''
  Contact result Enums for a job entry
  '''

  NONE = None
  FILED_BUT_NOT_HIRED = "Application/Resume Filed But Not Hired"
  HIRED = "Hired"
  NOT_ACCEPTING = "Not Accepting Applications/Resumes"


class AddressControl():
    
    '''
    Methods for controlling an Address object.
    '''
    
    @classmethod
    def parse_us_address(cls, address) -> dict:
      '''
      Parse address elements from string into dict
      Only works correctly for U.S. addresses
      Can be used on any address and examined to see if it's a valid U.S. address (i.e. check if interpretation of U.S. state is valid)
      This is a wrapper around usaddress.parse() to fix its bad output

      Arguments:
        address : Address object
      Returns : dict object
        A cleaned U.S. address
      '''

      address = usaddress.parse(address)
      address = cls._clean_usaddress_parse(address)
      return address
    
    def _clean_usaddress_parse(address_parsed: list[tuple]) -> dict:
      '''
      Create a cleaned up dict of the parsed result of the usaddress package.

      Arguments:
        address_parsed : usaddress obj
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
    
    @classmethod
    def build_street_address_from_cleaned_address_dict(cls, address_dict) -> str:
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
    

class Address(AddressControl):
    
    '''
    A standard U.S. address comprised of separated address components.
    Only contains components that are required for ReEmployCT entries.

    Intakes a raw address string in any format then parses and cleans it
    '''

    def __init__(self, address_raw: str) -> None:
      super().__init__()
      parsed = self.parse_us_address(address_raw)
      self.full_address = address_raw
      self.address_line_1 = self.build_street_address_from_cleaned_address_dict(parsed)
      # self.address_line_2 = ''
      self.city = parsed[Address_RequiredComponents.PLACE_NAME.value]

      self.state = parsed[Address_RequiredComponents.STATE_NAME.value]
      if(len(self.state) == 2):
        self.state = self.state.upper()
      else:
        self.state = self.state.title()

      self.zip = parsed[Address_RequiredComponents.ZIP_CODE.value]
    
    def full_state_name(self) -> str:
      '''
      Return full name of state from its letter abbreviation.
      '''

      if(len(self.state) > 2):
        return self.state
      
      return stateDictionary.States[self.state].value
    
    def abbrev_state_name(self) -> str:
      '''
      Return abbreviation letter name of state from its full name.
      '''

      if(len(self.state) == 2):
        return self.state
      
      return stateDictionary.States(self.state).name


class Address_RequiredComponents(ExtendedEnum):

  '''
  Required address components for entries in ReEmployCT (usaddress package format).
  '''

  ADDRESS_LINE_1 = 'AddressLine1' # assembled from build_street_address_from_cleaned_address_dict()
  PLACE_NAME = 'PlaceName' # City
  STATE_NAME = 'StateName'
  ZIP_CODE = 'ZipCode'
