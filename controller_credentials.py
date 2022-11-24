# Creates a credential file.
from cryptography.fernet import Fernet
import ctypes
import time
import os
import sys
from datetime import datetime, timedelta
import colorama
from getpass import getpass

class Credentials():

    def __init__(self):
        self.__username = ""
        self.__key = ""
        self.__password = ""
        self.__ssn = ""
        self.__key_file = 'key.key'
        self.__credentials_expiration = -1

    def gen_key(self):
        if(self._Credentials__key == ''):
            self.__key = Fernet.generate_key()
        return Fernet(self.__key)

    def encrypt_value(self, value, fernetKey):
        return fernetKey.encrypt(value.encode()).decode()
    
#----------------------------------------
# Getter setter for attributes
#----------------------------------------

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        while (username == ''):
            username = input('Enter a proper User name, blank is not accepted:')
        self.__username = username

    @property
    def password(self):
        return self.get_decoded_value('password')

    @password.setter
    def password(self, password):
        f = self.gen_key()
        self.__password = self.encrypt_value(password, f)
        del f
    
    @property
    def ssn(self):
        return self.get_decoded_value('ssn')

    @ssn.setter
    def ssn(self, ssn):
        def ssn_format(str):
            return str.rstrip().replace('-', '')

        ssn = ssn_format(ssn)
        while(len(ssn) != 9 or not ssn.isdigit()):
            ssn = ssn_format(getpass("Invalid input.\nEnter social security number:"))
        f = self.gen_key()
        self.__ssn = self.encrypt_value(ssn, f)
        del f, ssn

    @property
    def ssn_last4(self):
        return self.ssn[-4:]

    @property
    def credentials_expiration(self):
        return self.__credentials_expiration

    @credentials_expiration.setter
    def credentials_expiration(self,exp_time):
        if(exp_time >= 2):
            self.__credentials_expiration = exp_time


    def create_cred(self):
        """
        Encrypts password.
        Creates key file for storing the key.
        Create credential file with user name, and encrypted password and SSN.
        """

        CRED_FILENAME = 'credFile.ini'
        KEYS = [
            'username',
            'password',
            'ssn',
            'credentials_expiration',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'mother\'s_maiden_name',
            'date_of_birth',
            'driver\'s_license/state_ID_number',
            'driver\'s_license/state_ID_number_expiration'
        ]

        credStr = ''
        for key in KEYS:
            credStr += key + '=\n' 

        with open(CRED_FILENAME,'w') as file_in:
            file_in.write("username={}\npassword={}\nssn={}\ncredentials_expiration={}\n"
            .format(self.__username, self.__password, self.__ssn, self.__credentials_expiration))
            file_in.write("++"*20)


        # if there exists an older key file, remove it
        if(os.path.exists(self.__key_file)):
            os.remove(self.__key_file)

        # open the key.key file and place the key in it
        # the key file is hidden
        try:
            os_type = sys.platform
            if (os_type == 'linux'):
                self.__key_file = '.' + self.__key_file

            with open(self.__key_file,'w') as key_in:
                key_in.write(self.__key.decode())
                # hiding the key file
                # the below code snippet finds out which current os the script is running on and does the task base on it
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
        self.__ssn = ""
        self.__key = ""
        self.__key_file

    def rebuild_creds_from_file(self, cred_filename):
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

        self.__username = creds['username']
        self.__password = creds['password']
        self.__ssn = creds['ssn']
        self.__credentials_expiration = creds['credentials_expiration']

    def are_creds_expired(self):
        if(self.credentials_expiration == '-1' or time.time() <= float(self.credentials_expiration)): # -1 means credentials never expire
            return False
        return True
    
    def expire_time(self):
        return {
            'unix': self.credentials_expiration,
            'formatted': (datetime.fromtimestamp(float(self.credentials_expiration))).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_decoded_value(self, valueKey):
        '''
        Find the desired value from the .ini credentials file based on the given key (key value pair).
        '''

        with open("key.key", "r") as key_in:
            encryption_key = key_in.read().encode()

        f = Fernet(encryption_key)
        with open('credFile.ini', 'r') as cred_in:
            lines = cred_in.readlines()
            config = {}
            for line in lines:
                tuples = line.rstrip('\n').split('=', 1)
                if tuples[0] == valueKey:
                    config[tuples[0]] = tuples[1]
                    return f.decrypt(config[valueKey].encode()).decode()


def create_user_credentials():
    print(colorama.Fore.GREEN + "\nEnter your DOL ReEmployCT credentials (encrypted and stored locally)..." + colorama.Style.RESET_ALL)
    main()


def main():
    creds = Credentials()

    # accepting credentials
    creds.username = input("Enter UserName:")
    creds.password = getpass("Enter Password:")
    creds.ssn = getpass("Enter social security number:")
    print("Enter the expiry time for key file in minutes, [default:Will never expire]")
    
    # unix timestamp
    expiry_minutes = float(input("Enter time:") or '-1')
    if(expiry_minutes == -1):
        timestamp = expiry_minutes
    else:
        timestamp = time.time() + expiry_minutes * 60

    creds.credentials_expiration = timestamp
    

    # Calling the Credit
    creds.create_cred()
    print("**"*20)
    print("Cred file created successfully at {}".format(time.ctime()))
    print("**"*20)

if __name__ == "__main__":
    main()
