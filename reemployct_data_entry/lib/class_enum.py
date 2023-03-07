from enum import Enum


class ExtendedEnum(Enum):
    
    @classmethod
    def key_list(cls):
        '''
        Return list of all the Enums' keys
        '''
        return list(map(lambda c: c.name, cls))

    @classmethod
    def value_list(cls):
        '''
        Return list of all the class Enums' values
        '''
        return list(map(lambda c: c.value, cls))
    
    def value_attrib(self):
      '''
      Return called Enum's value as lowercase and whitespace converted to underscores.
      This is for converting to the syntax of an object's attribute name so they can be accessed.
      e.g. 'Employer Name' -> 'employer_name' which can be used to access an instance attrib like `abc.employer_name`.
      Implementation example: some_dict.__getattribute__(SomeEnum.EMPLOYER_NAME.value_attrib())
      '''
      return self.value.replace(' ', '_').lower()
