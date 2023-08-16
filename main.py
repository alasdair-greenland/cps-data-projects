import pandas as pd
import os
import re

#List of all employee position roster csv files
EPR_CSV_LIST = filter(lambda x: x.startswith("employeepositionroster"), os.listdir("data"))

# currently missing 2014 and 2015
# this is because my wifi stopped working when I was trying to download + convert them
# will add those asap

"""
for file in EPR_CSV_LIST:
  df = pd.read_csv(f'data/{file}')
  df.drop("Unnamed: 0", inplace=True, axis=1)
  df["Annual Salary"] = df["Annual Salary"].apply(lambda x: str(x).replace(",", ""))
  df["FTE Annual Salary"] = df["FTE Annual Salary"].apply(lambda x: str(x).replace(",", ""))
  df["Annual Benefit Cost"] = df["Annual Benefit Cost"].apply(lambda x: str(x).replace(",", ""))
  df.to_csv(f'data/{file}', index=False)
"""

def salary_report(df):
  """
  Takes in a dataframe representing part of an employee position roster.
  Returns a dict containing some useful datapoints about that dataframe.
  """
  df["Annual Salary"] = df["Annual Salary"].astype(float)
  df = df.dropna()
  df = df.sort_values("Annual Salary", ascending=False)
  # sort table by the annual salary of the employees
  return {
    "Average Salary": df["Annual Salary"].mean(),
    "Highest Salary": df["Annual Salary"].iat[0],
    "Highest Paid Position No.": df["Pos #"].iat[0],
    "Lowest Salary": df["Annual Salary"].iat[-1],
    "Lowest Paid Position No.": df["Pos #"].iat[-1]
  }

def get_salary(df, posno):
  """
  Returns the salary corresponding to the given position number
  """
  return df.loc[df["Pos #"] == posno]["Annual Salary"].iat[0]

def all_years(fn, *args):
  """
  Runs fn on all employee position rosters
  Returns a dictionary mapping the date of that roster to the result of the
  function
  """
  out = {}
  for df_name in EPR_CSV_LIST:
    df = pd.read_csv(f'data/{df_name}')
    date = re.split("[._]", df_name)[1]
    out[date] = fn(df, *args)
  return out

def pretty_print_dict(dc):
  pretty_print_dict_r(dc, "dict", 2)

def pretty_print_dict_r(dc, prevkey, indent):
  print((" " * (indent - 2)) + prevkey + ": {")
  for (key, val) in dc.items():
    if type(val) is dict:
      pretty_print_dict_r(val, key, indent + 2)
    else:
      print((" " * indent) + key + ": " + str(val) + ",")
  print((" " * (indent - 2)) + "},")

pretty_print_dict(all_years(salary_report))