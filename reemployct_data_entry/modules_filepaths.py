import os
import sys

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

def dynamic_full_path(filename) -> str:
    '''
    Returns the full absolute system filename path from a given relative filename path.
    The given relative filename path must be valid.
    The returned filename path is constructed from the __file__ path of the file that called this function with the given filename path string appended.
        Arguments:
            filename : str obj
                The filename (including extension) of the file to be located.
                Must be a valid relative filename path.
    '''
    if(type(filename) is not str):
        raise TypeError('File name must be a string: ' + str(filename))

    # get path of file that called this function
    # effectively the same as calling __file__ from the desired file
    executing_file_path = os.path.realpath(sys.argv[0])
    executing_file_path = os.path.dirname(executing_file_path)
    
    full_path = os.path.join(executing_file_path, filename)

    if(not os.path.exists(full_path)):
        raise Exception('Filename path does not exist: ' + full_path)

    return full_path
