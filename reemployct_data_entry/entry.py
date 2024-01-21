import datetime
import json
import os

import colorama

from reemployct_data_entry import controller_credentials as credCon
from reemployct_data_entry import navigate_ReEmployCT, upgrade_check
from reemployct_data_entry.lib import filepaths
from reemployct_data_entry.lib import job_control
from reemployct_data_entry.lib import browser_control


def main():

    colorama.init() # init colored text to work on Windows
    
    upgrade_check.main()

    msg = '--- Automatic unemployment benefits data entry for the U.S. DOL ReEmploy CT for Firefox ---'
    browser_control.msg_colored(msg)

    # create job data filepath json file if missing
    JOB_FILEPATH_JSON = filepaths.dynamic_full_path('jobDataLocation.json')
    if(not filepaths.is_filepath_valid(JOB_FILEPATH_JSON)):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump({'filepath_jobData': ''}, file)
        print(colorama.Fore.GREEN + f"Created: {JOB_FILEPATH_JSON}" + colorama.Style.RESET_ALL)

    # get job data filepath from json
    with open(JOB_FILEPATH_JSON, 'r') as file:
        json_jobDataFilepath = json.load(file)

    # validate job data filepath
    updateJobFilepath = False
    while(not filepaths.is_job_data_filepath_valid(json_jobDataFilepath['filepath_jobData'])):
        json_jobDataFilepath['filepath_jobData'] = input(colorama.Fore.CYAN + "Enter the full filepath (including file extension) of your job data excel file: " + colorama.Style.RESET_ALL)
        updateJobFilepath = True

    # set json job data filepath in jobDataLocation.json
    if(updateJobFilepath):
        with open(JOB_FILEPATH_JSON, 'w') as file:
            json.dump(json_jobDataFilepath, file)


    ###################################
    # Manage User Credentials
    ###################################

    # if missing credential files, delete anything remaining, then recreate credentials
    CRED_FILE = filepaths.dynamic_full_path('credFile.ini')
    KEY_KEY = filepaths.dynamic_full_path('key.key')
    if(not os.path.exists(CRED_FILE) or not os.path.exists(KEY_KEY)):
        if(os.path.exists(CRED_FILE)):
            print(colorama.Fore.YELLOW + "Missing credential's key file. Deleting credentials file to reset." + colorama.Style.RESET_ALL)
            os.remove(CRED_FILE)
        elif(os.path.exists(KEY_KEY)):
            print(colorama.Fore.YELLOW + "Missing credentials file. Deleting credential's key file to reset.")
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

    jobs = job_control.Jobs(json_jobDataFilepath['filepath_jobData'])
    jobs.isolate_columns(job_control.Jobs_RequiredData)
    jobs.isolate_week(datetime.date.today() - datetime.timedelta(7))
    if(not jobs.target_week_has_jobs()): return
    jobs.sanitize()
    jobs.us_only_addresses()
    if(not jobs.target_week_has_jobs()): return
    jobs.portal_format()


    ############
    # Data Entry
    ############
    
    driver = navigate_ReEmployCT.navigate(creds, jobs)
    print(colorama.Fore.GREEN + "\nData entry finished.\n")
    input("Press Enter to quit..." + colorama.Style.RESET_ALL)
    driver.quit()

if(__name__ == "__main__"):
    main()
