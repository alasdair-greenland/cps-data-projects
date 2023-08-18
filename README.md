# cps-data-projects

The two main functions at the moment are all_years and analyze

All years applies a lookup function (the useful one at the moment is salary_report)
to every dataframe in the data folder. Analyze applies all years, and then analyzes
the trends it finds in that data, such as the rate of change in the past year, over
five years, and predicts the future value.

Both all years and analyze return nested dictionaries, so the function
pretty_print_dict is useful to display the results on a command line. It formats
the dictionaries in a much more readable way then simply converting them to strings