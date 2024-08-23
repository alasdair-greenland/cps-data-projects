# cps-data-projects

NOTES on data_processor.py (2024 code)

The functions in data_processor are used to generate the data in processed_data.
These functions take in the input data (the only thing the user has to do is
input employeepositionroster_{YEAR}-06-30.csv) and output the processed data.
The function make_new_year_data generates all the needed files for the new year,
once its employee position roster is uploaded.

Once the new year data has been generated, look for about 70% of the "Existed Last Year"
fields in processed_data/position_data/{YEAR}.csv to be True - if it's significantly fewer,
something about employee name formatting has likely changed and will need to be accounted for
in find_same_job (in utils.py)





NOTES on main.py (2023 code)

NOTE: This is specifically designed to work with the employee files
that are release yearly on june 30th
DO NOT upload files from other dates (if you must, rename them as if they were
06-30 files) because this will break things -- namely, the trend predictors.

The two main functions at the moment are all_years and analyze

all_years applies a lookup function (currently, salary_report and full_school_report)
to every employee roster file in the data folder. Analyze applies all years, and then
analyzes the trends it finds in that data, such as the rate of change in the past year,
over five years, and predicts the future value.

Both all_years and analyze return nested dictionaries, so the function
pretty_print_dict is useful to display the results on a command line. It formats
the dictionaries in a much more readable way then simply converting them to strings