# Connecticut Dep. of Labor ReEmployCT Automated Data Entry
[![Python application](https://github.com/ariffjeff/ReEmployCT-Data-Entry/actions/workflows/python-app.yml/badge.svg)](https://github.com/ariffjeff/ReEmployCT-Data-Entry/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/ariffjeff/ReEmployCT-Data-Entry/actions/workflows/python-publish.yml/badge.svg?branch=main)](https://github.com/ariffjeff/ReEmployCT-Data-Entry/actions/workflows/python-publish.yml)

A Python CLI that automates entry of unemployment benefits data (weekly work search and certification) into Connecticut's DOL [ReEmployCT portal](https://reemployct.dol.ct.gov). ([More information on ReEmployCT](https://portal.ct.gov/dol/Unemployment-Benefits))

Weekly job application data from an Excel file that the user actively maintains is accessed and automatically entered into ReEmployCT through a web browser instance controlled by Selenium. The program automates as much of the process as possible, such as login, data entry, page navigation, and secure user [credential handling](#user-credentials). The user will only need to interact for data entry review/confirmation and for captchas that need to be solved. Once the user finishes any required interaction then the program automatically takes back control. The program will walk you through setting everything up to get you on your way (see [Setup](#setup-python) first).

## Requirements
- Firefox
- Excel
- User job application data must only include U.S. addresses (ReEmployCT requirement)
- Minimum of 3 work searches (job applications) per week (ReEmployCT requirement)
- Currently only job applications are supported by this program as data entries into ReEmployCT from the Excel file. (Job applications are defined as "employer contacts" by CT DOL). In other words, a valid work search such as a job fair attendance can not be entered by this program and instead would need to be entered into ReEmployCT manually.

## How to use
### Video Tutorial
[Automated Connecticut Weekly Unemployment Benefits](https://www.youtube.com/watch?v=Ff6FEwIE0Bw)

### Install ([PyPI](https://pypi.org/project/reemployct-data-entry/))
`pip install reemployct-data-entry`



### Setup (Python)
You first need to get your copy of the Excel file that the program knows how to read job application data from:
```
from reemployct_data_entry import entry
```
This will import the module you'll use to run the program, but also provide you with the path to the provided Excel template. Make a copy of `workSearch_template.xlsx`, save it wherever (and rename it whatever) you want. Open your copy, remove the row that contains the example job application, and start adding your own data (in the same format as the example row).

Tip: You can use `CTRL` + `;` on a cell in Excel to enter the current date. The format is MM/DD/YYYY which is what the program expects.


### Run
You can either run from the CLI with:
```
entry.main()
```
Or simply click `entry.py` to run it.

## User Credentials
To make the entire process streamlined, you can save your ReEmployCT login credentials when prompted by the CLI. Your credentials are encrypted and stored locally in the project folder in `credFile.ini` (only the username is left as plaintext). The encryption key is stored in `key.key`. You also have the option when saving your credentials to set an expiry time so that you will need to save a new set of credentials on a certain date.

### Resetting saved credentials
1. Delete `credFile.ini` from the project folder
2. You will be prompted for new credentials when you run `entry.main()`
