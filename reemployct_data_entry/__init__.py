import colorama

PACKAGE_NAME = 'reemployct_data_entry'

# can't use stdlib importlib.metadata here because remote tests will fail due to needing the package build
__version__ = "2.0.3"

# on `import reemployct_data_entry`, print the excel job data template file path for user convenience
if __name__ == PACKAGE_NAME:
  from reemployct_data_entry.lib import filepaths

  EXCEL_FILENAME = 'workSearch_template.xlsx'
  excel_path = filepaths.dynamic_full_path(EXCEL_FILENAME, validate=True)

  print(colorama.Fore.MAGENTA + f'\nJob data Excel template: {excel_path}' + colorama.Style.RESET_ALL)
