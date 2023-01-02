# on `import reemployct_data_entry`, print the excel job data template file path for user convenience
if __name__ == 'reemployct_data_entry':
  from reemployct_data_entry.lib import filepaths

  EXCEL_FILENAME = 'workSearch_template.xlsx'
  excel_path = filepaths.dynamic_full_path(EXCEL_FILENAME, validate=True)

  print('Job data Excel template: {}'.format(excel_path))
