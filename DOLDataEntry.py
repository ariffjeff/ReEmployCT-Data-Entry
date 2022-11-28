import pandas as pd
import json
from cryptography.fernet import Fernet
import os
import datetime
import navigate_ReEmployCT
import colorama
from selenium import webdriver
import modules_filepaths as m_fp
import controller_credentials as credCon
import wrangle_job_data as wrangle

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

    # validate job data filepath
    updateJobFilepath = False
    while(not m_fp.is_job_data_filepath_valid(json_jobDataFilepath['filepath_jobData'])):
        json_jobDataFilepath['filepath_jobData'] = input(colorama.Fore.GREEN + "Enter the filepath (including file extension) to your job data excel file: " + colorama.Style.RESET_ALL)
        updateJobFilepath = True

    # set json job data filepath in jobDataLocation.json
    if(updateJobFilepath):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump(json_jobDataFilepath, file)


    ###################################
    # Manage User Credentials
    ###################################

    # if missing credential files, delete anything remaining, then recreate credentials
    if(not os.path.exists('credFile.ini') or not os.path.exists('key.key')):
        if(os.path.exists('credFile.ini')):
            print("Missing credential's key file.\nDeleting credentials file to reset.")
            os.remove('credFile.ini')
        elif(os.path.exists('key.key')):
            print("Missing credentials file.\nDeleting credential's key file to reset.")
            os.remove('key.key')
        credCon.create_user_credentials()

    creds = credCon.Credentials()
    creds.rebuild_creds_from_file('credFile.ini')
    if(creds.are_creds_expired()):
        print("Your credentials expired on " + creds.expire_time()['formatted'])
        credCon.create_user_credentials()

    ##########
    # Job Data
    ##########

    table_jobs = pd.read_excel(json_jobDataFilepath['filepath_jobData'])
    table_jobs = wrangle.drop_bad_rows(table_jobs)
    last_week_day = datetime.date.today() - datetime.timedelta(7)
    target_week = wrangle.isolate_week_from_day(table_jobs, last_week_day)

    ############
    # Data Entry
    ############

    # check if there is any job data for target week
    if(len(target_week['table_jobs']) == 0):
        print(colorama.Fore.RED +
        "\n*** You have no days of job data to enter for the target week! ({} - {}) ***\nQuitting script.".format(target_week['day_start.date()'], target_week['day_end.date()'])
        + colorama.Style.RESET_ALL)
        return
    
    driver = navigate_ReEmployCT.navigate(creds, target_week['table_jobs'])
    print(colorama.Fore.GREEN + "\nData entry finished. Quitting.\n" + colorama.Style.RESET_ALL)
    driver.quit()

if(__name__ == "__main__"):
    main()
