# Creates a credential file.
from cryptography.fernet import Fernet
import re
import ctypes
import time
import os
import sys
from datetime import datetime, timedelta

class Credentials():

    def __init__(self):
        self.__username = ""
        self.__key = ""
        self.__password = ""
        self.__key_file = 'key.key'
        self.__time_of_exp = -1

#----------------------------------------
# Getter setter for attributes
#----------------------------------------

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self,username):
        while (username == ''):
            username = input('Enter a proper User name, blank is not accepted:')
        self.__username = username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self,password):
        self.__key = Fernet.generate_key()
        f = Fernet(self.__key)
        self.__password = f.encrypt(password.encode()).decode()
        del f

    @property
    def expiry_time(self):
        return self.__time_of_exp

    @expiry_time.setter
    def expiry_time(self,exp_time):
        if(exp_time >= 2):
            self.__time_of_exp = exp_time


    def create_cred(self):
        """
        This function is responsible for encrypting the password and create key file for
        storing the key and create a credential file with user name and password
        """

        cred_filename = 'CredFile.ini'

        with open(cred_filename,'w') as file_in:
            file_in.write("#Credential file:\nUsername={}\nPassword={}\nExpiry={}\n"
            .format(self.__username,self.__password,self.__time_of_exp))
            file_in.write("++"*20)


        # If there exists an older key file, This will remove it.
        if(os.path.exists(self.__key_file)):
            os.remove(self.__key_file)

        # Open the Key.key file and place the key in it.
        # The key file is hidden.
        try:

            os_type = sys.platform
            if (os_type == 'linux'):
                self.__key_file = '.' + self.__key_file

            with open(self.__key_file,'w') as key_in:
                key_in.write(self.__key.decode())
                # Hidding the key file.
                # The below code snippet finds out which current os the script is running on and does the task base on it.
                if(os_type == 'win32'):
                    ctypes.windll.kernel32.SetFileAttributesW(self.__key_file, 2)
                else:
                    pass

        except PermissionError:
            os.remove(self.__key_file)
            print("A Permission error occurred.\n Please rerun the script")
            sys.exit()

        self.__username = ""
        self.__password = ""
        self.__key = ""
        self.__key_file

    def rebuild_cred_from_file(self, cred_filename):
        '''
        Recreate credentials object from credentials file.
        '''

        with open(cred_filename, 'r') as cred_in:
            lines = cred_in.readlines()
            creds = {}
            for line in lines:
                tuples = line.rstrip('\n').split('=', 1)
                if(len(tuples) == 2):
                    creds[tuples[0]] = tuples[1]

        self.__username = creds['Username']
        self.__password = creds['Password']
        self.__time_of_exp = creds['Expiry']

    def are_creds_expired(self):
        if(self.expiry_time == '-1' or time.time() <= float(self.expiry_time)): # -1 means credentials never expire
            return False
        return True
    
    def expire_time(self):
        return {
            'unix': self.expiry_time,
            'formatted': (datetime.fromtimestamp(float(self.expiry_time))).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_decoded_password(self):
        with open("key.key", "r") as key_in:
            key = key_in.read().encode()

        f = Fernet(key)
        with open('CredFile.ini', 'r') as cred_in:
            lines = cred_in.readlines()
            config = {}
            for line in lines:
                tuples = line.rstrip('\n').split('=', 1)
                if tuples[0] in ('Username', 'Password'):
                    config[tuples[0]] = tuples[1]
        
            return f.decrypt(config['Password'].encode()).decode()



def main():
    creds = Credentials()

    # accepting credentials
    creds.username = input("Enter UserName:")
    creds.password = input("Enter Password:")
    print("Enter the epiry time for key file in minutes, [default:Will never expire]")
    
    # unix timestamp
    expiry_minutes = float(input("Enter time:") or '-1')
    if(expiry_minutes == -1):
        timestamp = expiry_minutes
    else:
        timestamp = time.time() + expiry_minutes * 60

    creds.expiry_time = timestamp
    

    # Calling the Credit
    creds.create_cred()
    print("**"*20)
    print("Cred file created successfully at {}".format(time.ctime()))

    if not(creds.expiry_time == -1):
        os.startfile('expire.py')

    print("**"*20)

if __name__ == "__main__":
    main()
