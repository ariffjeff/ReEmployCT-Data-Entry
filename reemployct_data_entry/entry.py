import datetime
import json
import os

import colorama
import pandas as pd

from reemployct_data_entry import controller_credentials as credCon
from reemployct_data_entry import navigate_ReEmployCT
from reemployct_data_entry.lib import filepaths as m_fp
from reemployct_data_entry.lib import webdriver as m_driver
from reemployct_data_entry.lib import wrangle_job_data as wrangle


def main():
    colorama.init() # init colored text to work on Windows
    msg = '--- Automatic unemployment benefits data entry for the U.S. DOL ReEmploy CT for Firefox ---'
    m_driver.msg_user_verify_entries(msg)

    # create job data filepath json file if missing
    JOB_FILEPATH_JSON = m_fp.dynamic_full_path('jobDataLocation.json')
    if(not m_fp.is_filepath_valid(JOB_FILEPATH_JSON)):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump({'filepath_jobData': ''}, file)
        print("Created: {}".format(JOB_FILEPATH_JSON))

    # get job data filepath from json
    with open(JOB_FILEPATH_JSON, 'r') as file:
        json_jobDataFilepath = json.load(file)

    # validate job data filepath
    updateJobFilepath = False
    while(not m_fp.is_job_data_filepath_valid(json_jobDataFilepath['filepath_jobData'])):
        json_jobDataFilepath['filepath_jobData'] = input(colorama.Fore.GREEN + "Enter the full filepath (including file extension) of your job data excel file: " + colorama.Style.RESET_ALL)
        updateJobFilepath = True

    # set json job data filepath in jobDataLocation.json
    if(updateJobFilepath):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump(json_jobDataFilepath, file)


    ###################################
    # Manage User Credentials
    ###################################

    # if missing credential files, delete anything remaining, then recreate credentials
    CRED_FILE = m_fp.dynamic_full_path('credFile.ini')
    KEY_KEY = m_fp.dynamic_full_path('key.key')
    if(not os.path.exists(CRED_FILE) or not os.path.exists(KEY_KEY)):
        if(os.path.exists(CRED_FILE)):
            print("Missing credential's key file.\nDeleting credentials file to reset.")
            os.remove(CRED_FILE)
        elif(os.path.exists(KEY_KEY)):
            print("Missing credentials file.\nDeleting credential's key file to reset.")
            os.remove(KEY_KEY)
        credCon.create_user_credentials()

    creds = credCon.Credentials()
    creds.rebuild_creds_from_file(CRED_FILE)
    if(creds.are_creds_expired()):
        print("Your credentials expired on " + creds.expire_time()['formatted'])
        credCon.create_user_credentials()

    ##########
    # Job Data
    ##########

    table_jobs = pd.read_excel(json_jobDataFilepath['filepath_jobData'])
    table_jobs = wrangle.drop_bad_rows(table_jobs)
    target_week = wrangle.isolate_week_from_day(table_jobs,  datetime.date.today() - datetime.timedelta(7)) # last week

    ############
    # Data Entry
    ############

    if not wrangle.target_week_has_job_data(target_week):
        return
    
    driver = navigate_ReEmployCT.navigate(creds, target_week['table_jobs'])
    print(colorama.Fore.GREEN + "\nData entry finished. Quitting.\n" + colorama.Style.RESET_ALL)
    driver.quit()

if(__name__ == "__main__"):
    main()
