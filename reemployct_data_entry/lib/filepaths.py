import os
import inspect


def is_job_data_filepath_valid(filepath):
    if(not os.path.isfile(filepath) or os.path.splitext(filepath)[-1] != ".xlsx"):
        if(len(filepath) == 0): # mainly for when initial package gets installed and there is no path set
            print("No user job data excel file found.")
            return False
        print("No user job data excel file found: {}".format(filepath))
        return False
    print("User job data excel file found: {}".format(filepath))
    return True

def is_filepath_valid(filepath):
    if(not os.path.isfile(filepath)):
        print("No user job data .json config found: {}".format(filepath))
        return False
    print("User job data config found: {}".format(filepath))
    return True

def dynamic_full_path(filename, validate=False) -> str:
    '''
    Returns the full absolute system filename path from a given relative filename path.
    The given relative filename path should be valid or valid in the future when the path is called upon (e.g. path to the key.key that hasn't been created yet).
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
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    path = os.path.dirname(mod.__file__)
    
    full_path = os.path.join(path, filename)

    # no need to check path validity in some cases since some files that paths point to intenionally don't exist and are created in the future (such as cred file initialization)
    if(validate and not os.path.exists(full_path)):
        raise Exception('Filepath does not exist: ' + full_path)

    return full_path
