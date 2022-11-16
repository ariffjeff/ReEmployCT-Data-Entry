import pandas as pd
import json
import credentialsController as credCon
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
import datetime
import navigate_ReEmployCT
import colorama
from selenium import webdriver
import modules_filepaths as m_fp

def main():
    print(colorama.Fore.GREEN + "\n")
    print("-"*91)
    print("--- Automatic unemployment benefits data entry for the U.S. DOL ReEmploy CT for Firefox ---")
    print("-"*91)
    print(colorama.Style.RESET_ALL + "\n")

    # create job data filepath json file if missing
    JOB_FILEPATH_JSON = "jobDataLocation.json"
    if(not m_fp.is_filepath_valid(JOB_FILEPATH_JSON)):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump({'filepath_jobData': ''}, file)

    # get job data filepath from json
    with open(JOB_FILEPATH_JSON, 'r') as file:
        json_jobDataFilepath = json.load(file)

    def does_job_data_file_exist(filepath):
        if(not os.path.isfile(filepath) or os.path.splitext(filepath)[-1] != ".xlsx"):
            print("No user job data excel file found.")
            return False
        print("Job data excel found at: \"" + filepath + "\"")
        return True

    # validate job data filepath
    updateJobFilepath = False
    while(not does_job_data_file_exist(json_jobDataFilepath['filepath_jobData'])):
        json_jobDataFilepath['filepath_jobData'] = input(colorama.Fore.GREEN + "Enter the filepath (including file extension) to your job data excel file: " + colorama.Style.RESET_ALL)
        updateJobFilepath = True

    # set json job data filepath in jobDataLocation.json
    if(updateJobFilepath):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump(json_jobDataFilepath, file)


    ###################################
    # Job Data
    ###################################

    table_jobs = pd.read_excel(json_jobDataFilepath['filepath_jobData'])

    # clean table - drop rows of bad types
    table_jobs['Date of Work Search'] = table_jobs['Date of Work Search'].apply(lambda x: pd.to_datetime(x, errors='coerce')) # sets bad values to None/NaN/NaT for easy parsing
    index_NaT = table_jobs.loc[pd.isna(table_jobs["Date of Work Search"]), :].index # get array of indices of rows where data is of None/NaN/NaT
    table_jobs = table_jobs.drop(table_jobs.index[index_NaT]) # drop rows

    # ask user which week (sunday - saturday) they want to enter data for

    # isolate rows of target week
    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 # SUN = 0 ... SAT = 6
    last_week_start = pd.Timestamp(today - timedelta(7 + idx)) # sunday
    last_week_end = pd.Timestamp(last_week_start + timedelta(6)) # saturday
    target_days = table_jobs['Date of Work Search'].between(last_week_start, last_week_end) # marks target days as True
    target_week = table_jobs.loc[target_days == True] # isolate target week rows
    target_week.reset_index(inplace=True)

    ###################################
    # Manage User Credentials
    ###################################

    def create_user_credentials():
        print(colorama.Fore.GREEN + "\nEnter your DOL ReEmployCT credentials (encrypted and stored locally)..." + colorama.Style.RESET_ALL)
        credCon.main()

    # if missing credential files, delete anything remaining, then recreate credentials
    if(not os.path.exists('credFile.ini') or not os.path.exists('key.key')):
        if(os.path.exists('credFile.ini')):
            print("Missing credential's key file.\nDeleting credentials file to reset.")
            os.remove('credFile.ini')
        elif(os.path.exists('key.key')):
            print("Missing credentials file.\nDeleting credential's key file to reset.")
            os.remove('key.key')
        create_user_credentials()

    creds = credCon.Credentials()
    creds.rebuild_creds_from_file('credFile.ini')
    if(creds.are_creds_expired()):
        print("Your credentials expired on " + creds.expire_time()['formatted'])
        create_user_credentials()

    ############
    # Data Entry
    ############

    # check if there is any job data for target week
    if(len(target_week) == 0):
        print(colorama.Fore.RED +
        "\n*** You have no days of job data to enter for the target week! ({} - {}) ***\nQuitting script.".format(last_week_start.date(), last_week_end.date())
        + colorama.Style.RESET_ALL)
        return
    
    driver = navigate_ReEmployCT.enterData(creds, target_week)
    driver.quit()
    print("Data entry finished.")

if(__name__ == "__main__"):
    main()
