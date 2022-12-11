import unittest
import wrangle_job_data as wrangle
import usaddress

class Test_Address_Parsing(unittest.TestCase):

  def test_us_address_converts_to_expected_components(self):
    '''
    Ensure a given raw US address string (from the user excel data) is correctly parsed and
    converted to the exact components that would be entered into the CT DOL work search entry form.
    '''

    LABELS_REF = usaddress.LABELS # official US standard component names for reference 

    ADDRESS_INPUT = '11770 Haynes Bridge Road, Suite 205 - 371, Alpharetta, GA 30009, US'
    ADDRESS_EXPECTED_OUTPUT = {
      'address_line_1': '11770 Haynes Bridge Road', # custom assembled
      'PlaceName': 'Alpharetta',
      'StateName': 'Georgia',
      'ZipCode': '30009'
    }

    # create dict of US address components
    address_parsed = usaddress.parse(ADDRESS_INPUT)
    address_dict = wrangle.clean_usaddress_parse(address_parsed)
    address_dict['StateName'] = wrangle.state_abbrev_to_full_name(address_dict['StateName']) # Get state name or its abbreviation - MUST BE US ADDRESS
    address_line_1 = wrangle.build_address_from_cleaned_address_dict(address_dict)

    self.assertEqual(ADDRESS_EXPECTED_OUTPUT['address_line_1'], address_line_1)
    self.assertEqual(ADDRESS_EXPECTED_OUTPUT['address_line_1'], '11770 Haynes Bridge Road')
    self.assertEqual(ADDRESS_EXPECTED_OUTPUT['PlaceName'], 'Alpharetta')
    self.assertEqual(ADDRESS_EXPECTED_OUTPUT['StateName'], 'Georgia')
    self.assertEqual(ADDRESS_EXPECTED_OUTPUT['ZipCode'], '30009')

if __name__ == '__main__':
  unittest.main()
