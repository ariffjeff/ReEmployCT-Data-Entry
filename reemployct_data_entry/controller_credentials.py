# Creates a credential file.
import ctypes
import os
import sys
import time
from datetime import datetime
from getpass import getpass

import colorama
from cryptography.fernet import Fernet

from reemployct_data_entry.lib import filepaths as m_fp
from reemployct_data_entry.lib import webdriver as m_driver


class Encrypted_Property:
    ''' Creates user credential properties that are encrypted and handled via getter/setter functionality '''

    def __init__(self, cls, attr):
        self.attr = "_{}__".format(cls) + attr
    
    def __get__(self, instance, owner):
        value = instance.get_decrypted_value_from_cred_file(self.attr.replace('_{}__'.format(instance.__class__.__name__), ''))
        return value
    
    def __set__(self, instance, value):
        if(value == ''): # don't encrypt nothing (attr being created)
            setattr(instance, self.attr, value)
            return
        key = instance.get_encryption_key() # use any existing key
        if(key is not None):
            setattr(instance, '_{}__key'.format(instance.__class__.__name__), key) # encryption key
            f = Fernet(key)
        else:
            f = instance.gen_key()
        value = instance.encrypt_value(value, f)
        setattr(instance, self.attr, value)


class Credentials():
    ''' Creates and manages user credentials '''

    def gen_key(self):
        ''' Generates an encryption key, which is set to the __key attr. Returns a Fernet object based on the key. '''
        if(self._Credentials__key == ''):
            self.__key = Fernet.generate_key()
        return Fernet(self.__key)

    def encrypt_value(self, value, fernetKey):
        return fernetKey.encrypt(value.encode()).decode()

    def __init__(self):
        # attrs with no __ prefix are controlled by Encrypted_Property
        self.__username = ""
        self.__key = ""
        self.password = ""
        self.__ssn = ""
        self.__key_file = m_fp.dynamic_full_path('key.key')
        self.__credentials_expiration = -1

        # weekly certification correction - https://ctdolcontactcenter.force.com/submit/s/claim-filing-and-payment
        self.name_first = ''
        self.name_last = ''
        self.phone_number = ''
        self.email = ''
        self.name_mothers_maiden = ''
        self.date_of_birth = ''
        self.drivers_license_state_ID_number = ''
        self.drivers_license_state_ID_number_expiration = ''
    
    #----------------------------------------
    # Getter setter for attributes
    #----------------------------------------
    
    # ONLY encrypted properties that all share the exact same getter/setter functionality from Encrypted_Property
    ENCRYPTED_PROPERTIES = [
        'password',
        'name_first',
        'name_last',
        'phone_number',
        'email',
        'name_mothers_maiden',
        'date_of_birth',
        'drivers_license_state_ID_number',
        'drivers_license_state_ID_number_expiration'
    ]

    # create encrypted properties
    for prop in ENCRYPTED_PROPERTIES:
        vars()[prop] = Encrypted_Property(__qualname__, prop)
    del ENCRYPTED_PROPERTIES
    del prop

    # create encrypted properties that need unique handling
    @property
    def ssn(self):
        return self.get_decrypted_value_from_cred_file('ssn')

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

    # create non-encrypted properties
    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        while (username == ''):
            username = input('Enter a proper User name, blank is not accepted:')
        self.__username = username
    
    @property
    def credentials_expiration(self):
        return self.__credentials_expiration

    @credentials_expiration.setter
    def credentials_expiration(self,exp_time):
        if(exp_time >= 2):
            self.__credentials_expiration = exp_time

    def ini_file_keys(self):
        '''
        Returns only the keys from __init__ that should be output to the credentials ini file
        '''
        KEYS_TO_OUTPUT_TO_INI_FILE = [
            'username',
            'password',
            'ssn',
            'credentials_expiration',
            'name_first',
            'name_last',
            'phone_number',
            'email',
            'name_mothers_maiden',
            'date_of_birth',
            'drivers_license_state_ID_number',
            'drivers_license_state_ID_number_expiration'
        ]
        return KEYS_TO_OUTPUT_TO_INI_FILE

    def create_formatted_cred_output_string(self):
        '''
        Create formatted output string of credential key and value data for .ini file based on __init__ attribs
        '''
        credStr = ''
        PREFIX = '_Credentials__'
        for key in self.ini_file_keys():
            if(PREFIX + key in self.__dict__): # get class' __init__ attribs
                value = self.__dict__[PREFIX + key]
                credStr += key + '=' + str(value) + '\n'
        return credStr

    def create_credentials_file(self):
        """
        Creates key file for storing the key.
        Creates credential file with encrypted credentials.
        """

        CRED_FILENAME = m_fp.dynamic_full_path('credFile.ini')
        credStr = self.create_formatted_cred_output_string()
        with open(CRED_FILENAME,'w') as file_in:
            file_in.write(credStr)
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

            # file contents aren't written until with block ends
            with open(self.__key_file,'w') as key_in: # creates a file if non exists
                # key = self.__key.decode() # explicit declaration to potentially avoid strange non-assignment problems regarding __x and _Credentials__x lookups
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
        Reads the contents of a credentials file then sets the property values of a credentials instance.
        '''

        if(not os.path.exists(cred_filename)):
            return

        # create dict from ini file keys and values
        with open(cred_filename, 'r') as cred_in:
            lines = cred_in.readlines()
            creds = {}
            for line in lines:
                tuples = line.rstrip('\n').split('=', 1)
                if(len(tuples) == 2):
                    creds[tuples[0]] = tuples[1]

        # assign values to mangled-name (__x) variables. vars with @property defs get their regular var equivalents updated automatically as well.
        for key in creds:
            setattr(self, '_{}__'.format(__class__.__name__) + key, creds[key])
        
    def are_creds_expired(self):
        if(self.credentials_expiration == '-1' or time.time() <= float(self.credentials_expiration)): # -1 means credentials never expire
            return False
        return True
    
    def expire_time(self):
        return {
            'unix': self.credentials_expiration,
            'formatted': (datetime.fromtimestamp(float(self.credentials_expiration))).strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_encryption_key(self, key_file=None):
        if(key_file is None):
            key_file = m_fp.dynamic_full_path('key.key')

        if(not os.path.exists(key_file)):
            return None

        with open(key_file, "r") as key_in:
            encryption_key = key_in.read().encode()
        return encryption_key
    
    def get_decrypted_value_from_cred_file(self, valueKey):
        '''
        Find the desired value from the .ini credentials file based on the given key (key value pair).
        '''

        encryption_key = self.get_encryption_key()
        f = Fernet(encryption_key)
        with open(m_fp.dynamic_full_path('credFile.ini'), 'r') as cred_in:
            lines = cred_in.readlines()
            config = {}
            for line in lines:
                tuples = line.rstrip('\n').split('=', 1)
                if tuples[0] == valueKey:
                    config[tuples[0]] = tuples[1]
                    if(config[valueKey] == None or len(config[valueKey]) == 0): return config[valueKey] # avoid error of decrypting empty string/no value
                    return f.decrypt(config[valueKey].encode()).decode()
    
    def are_work_search_correction_creds_set(self) -> bool:
        ''' Checks if a required credential exists (has user entered data) for the work search correction web pages '''
        if(self.name_first == ''):
            return False
        return True


def create_user_credentials():
    ''' Gets credentials for the DOL ReEmployCT portal from the user and saves them to the .ini creds file '''
    print(colorama.Fore.GREEN + "\nEnter your DOL ReEmployCT credentials (encrypted and stored locally)..." + colorama.Style.RESET_ALL)
    creds = Credentials()
    creds.rebuild_creds_from_file(m_fp.dynamic_full_path('credFile.ini'))

    # accepting credentials
    creds.username = input("Username:")
    creds.password = getpass("Password:")
    creds.ssn = getpass("Social Security Number:")
    print("Enter the expiry time for key file in minutes, [default:Will never expire]")
    
    # unix timestamp
    expiry_minutes = float(input("Enter time:") or '-1')
    if(expiry_minutes == -1):
        timestamp = expiry_minutes
    else:
        timestamp = time.time() + expiry_minutes * 60

    creds.credentials_expiration = timestamp
    
    creds.create_credentials_file()
    m_driver.msg_user_verify_entries("Cred file created successfully at {}".format(time.ctime()), "green")

def create_correction_user_credentials():
    '''
    Gets credentials for the corrections page from the user and saves them to the .ini creds file
    https://ctdolcontactcenter.force.com/submit/s/claim-filing-and-payment
    '''

    print(colorama.Fore.GREEN + "\nEnter your DOL credentials (encrypted and stored locally)..." + colorama.Style.RESET_ALL)
    creds = Credentials()
    creds.rebuild_creds_from_file(m_fp.dynamic_full_path('credFile.ini'))

    creds.name_first = input('First Name:')
    creds.name_last = input('Last Name:')
    creds.phone_number = input('Phone Number:')
    creds.email = input('Email:')
    if(creds.ssn == ''):
        creds.ssn = getpass('Social Security Number:')
    creds.name_mothers_maiden = input('Mother\'s Maiden Name:')
    creds.date_of_birth = input('Date of Birth (MM/DD/YYYY):')
    creds.drivers_license_state_ID_number = input('Driver\'s License/State ID Number:')
    creds.drivers_license_state_ID_number_expiration = input('Driver\'s License Expiration Date/State ID (MM/DD/YYYY):')
    
    creds.create_credentials_file()

    print("**"*20)
    print("Cred file created successfully at {}".format(time.ctime()))
    print("**"*20)

if __name__ == "__main__":
    create_user_credentials()
