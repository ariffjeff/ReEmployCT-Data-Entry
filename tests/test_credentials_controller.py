import unittest

from reemployct_data_entry import controller_credentials as cc


class TestCredCon(unittest.TestCase):

  def test_formattedCredStringIniOutput(self):
    '''
    Ensure the number of formatted output keys in the .ini credentials file equals the number of corresponding name-matching attributes from __init__
    Assertion would fail when any of the key names in userCreds.ini_file_keys() are not written exactly the same as the corresponding attribute names from __init__
    This is to force name parity between the desired credential key attribs in __init__ and the keys that actually output to the .ini file in order to reduce complexity
    For example, this unit test fails if the __init__ key name_first is written as first_name in userCreds.ini_file_keys()
    '''
    userCreds = cc.Credentials()
    formatted_credential_string = userCreds.create_formatted_cred_output_string()
    KEYS = userCreds.ini_file_keys()
    self.assertEqual(formatted_credential_string.rstrip('\n').count('\n') + 1, len(KEYS))


if __name__ == '__main__':
  unittest.main()
