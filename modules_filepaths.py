import os

def is_job_data_filepath_valid(filepath):
    if(not os.path.isfile(filepath) or os.path.splitext(filepath)[-1] != ".xlsx"):
        print("No user job data excel file found.")
        return False
    print("Job data excel found at: \"" + filepath + "\"")
    return True

def is_filepath_valid(filepath):
    if(not os.path.isfile(filepath)):
        print("No user job data file found.")
        return False
    print("Job data found at: " + filepath)
    return True
