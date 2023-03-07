from enum import Enum


class ExtendedEnum(Enum):

    @classmethod
    def list_full(cls):
        '''
        Return list of all the full names of the states
        '''
        return list(map(lambda c: c.value, cls))
    
    @classmethod
    def list_abbrev(cls):
        '''
        Return list of all the abbreviated names of the states
        '''
        return list(map(lambda c: c.name, cls))


class States(ExtendedEnum):

    '''
    Enum of U.S. states that matches all those found in ReEmployCT
    '''

    AK = 'Alaska'
    AL = 'Alabama'
    AR = 'Arkansas'
    AZ = 'Arizona'
    CA = 'California'
    CO = 'Colorado'
    CT = 'Connecticut'
    DC = 'District Of Columbia'
    DE = 'Delaware'
    FL = 'Florida'
    GA = 'Georgia'
    GU = 'Guam'
    HI = 'Hawaii'
    IA = 'Iowa'
    ID = 'Idaho'
    IL = 'Illinois'
    IN = 'Indiana'
    KS = 'Kansas'
    KY = 'Kentucky'
    LA = 'Louisiana'
    MA = 'Massachusetts'
    MD = 'Maryland'
    ME = 'Maine'
    MI = 'Michigan'
    MN = 'Minnesota'
    MO = 'Missouri'
    MS = 'Mississippi'
    MT = 'Montana'
    NC = 'North Carolina'
    ND = 'North Dakota'
    NE = 'Nebraska'
    NH = 'New Hampshire'
    NJ = 'New Jersey'
    NM = 'New Mexico'
    NV = 'Nevada'
    NY = 'New York'
    OH = 'Ohio'
    OK = 'Oklahoma'
    OR = 'Oregon'
    PA = 'Pennsylvania'
    PR = 'Puerto Rico'
    RI = 'Rhode Island'
    SC = 'South Carolina'
    SD = 'South Dakota'
    TN = 'Tennessee'
    TX = 'Texas'
    UT = 'Utah'
    VA = 'Virginia'
    VI = 'Virgin Islands'
    VT = 'Vermont'
    WA = 'Washington'
    WI = 'Wisconsin'
    WV = 'West Virginia'
    WY = 'Wyoming'
