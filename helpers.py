import pandas as pd
import os
import re # regex
import requests as reqs
import random

from constants import *

def to_float(str):
  out = NO_DATA
  try:
    out = float(str)
  except:
    pass
  return out

def debug(msg):
  if DEBUG:
    print(msg)

def is_pos_new(sy, filters, posno):
  df2 = filter(pd.read_csv(f"data/employeepositionroster_{sy - 1}-06-30.csv"), filters)
  return not (posno in df2["Pos #"].unique())

def pos_removed(sy, filters, posno):
  """
  Returns True if the position didn't exist in the year after sy
  """
  if sy == CURRENT_YEAR:
    return False # assume it won't go away next year
  
  df = pd.read_csv(f"data/employeepositionroster_{sy + 1}-06-30.csv")
  df = filter(df, filters)
  return not (posno in df["Pos #"].unique())

def get_salary(sy, filters, posno):
  """
  Returns the salary corresponding to the given position number
  Returns as a dict with "Salary": val for compatibility reasons
  """
  df = pd.read_csv(f"data/employeepositionroster_{sy}-06-30.csv")
  df = filter(df, filters)
  return {
    "Salary": df.loc[df["Pos #"] == posno]["Annual Salary"].iat[0]
  }

def filter(df, filters):
  """
  Filters a dataframe to only keep rows where the value in column {key} is equal
  to one of the values in { [value] }
  """
  outdf = df
  for (key, lst) in filters.items():
    outdf = outdf.loc[outdf[key].isin(lst)]
  return outdf

def all_years(fn, filters, *args):
  """
  Runs fn on all employee position rosters
  Returns a dictionary mapping the date of that roster to the result of the
  function
  """
  out = {}
  for df_name in EPR_CSV_LIST:
    date = re.split("[._]", df_name)[1]
    sy = date.split("-")[0]
    out[date] = fn(int(sy), filters, *args)
  return out

def flip_sort(dc):
  """
  Expects a dictionary where the values are also dictionaries.
  Switches the keys of the inner dictionaries to the outer ones and vice versa

  for example:
  {
    a: { foo: 1, bar: 3 },
    b: { foo: 5, bar: 2 }
  }
  becomes
  {
    foo: { a: 1, b: 5 },
    bar: { a: 3, b: 2 }
  }
  """
  first = True
  out = {}
  for key, dc2 in dc.items():
    for key2, val in dc2.items():
      if first: out[key2] = {}
      out[key2][key] = val
    first = False
  return out

def safe_round(*args):
  """
  Rounds the number, or returns NO_DATA if the thing isn't a number
  """
  out = NO_DATA
  try:
    out = round(*args)
  except:
    pass
  return out

def round_if_number(*args):
  """
  Rounds the number, or returns the original input (args[0]) if not a number
  """
  out = args[0]
  try:
    out = round(*args)
  except:
    pass
  return out

def trends(dc):
  """
  Expects a dictionary whose keys are dates, specifically 20YY-06-30
  Only to be used internally, as a helper function for all_trends
  """
  out = {}
  lst = list(dc.keys())
  lst.sort()
  latest_date = lst[-1]

  year = int(latest_date.split("-")[0])
  out["Current Value"] = safe_round(dc[latest_date], 1)
  out["Last Year"] = safe_round(dc[f'{year - 1}-06-30'], 1)
  out["5 Years Ago"] = safe_round(dc[f'{year - 5}-06-30'], 1)

  pct1 = 0
  if out["Last Year"] == NO_DATA:
    out["Change since last year"] = "N/A"

  else:
    delta1 = out["Current Value"] - out["Last Year"]
    pct1 = delta1 / out["Last Year"]
    pct1 = round(pct1 * 100, 1)

    out["Change since last year"] = f'{round(delta1, 1)} ({pct1}%)'

  pct2 = 0
  if out["5 Years Ago"] == NO_DATA:
    out["Change over 5 years"] = "N/A"

  else:
    delta2 = out["Current Value"] - out["5 Years Ago"]
    pct2 = delta2 / out["5 Years Ago"]
    pct2 = round(pct2 * 100, 1)

    out["Change over 5 years"] = f'{round(delta2, 1)} ({pct2}%)'

  sign2 = 1
  if pct2 != 0:
    sign2 = pct2 / abs(pct2) # the sign of the second percentage
  avg_of_five_year_rate = abs(pct2) ** 0.2
  avg_of_five_year_rate *= sign2

  avg_change = (avg_of_five_year_rate + pct1) / 2
  # the average of:
  #   the geometric mean of the 5 year rate of change and
  #   the one year rate of change

  if out["5 Years Ago"] == NO_DATA:
    avg_change = pct1
  
  if out["Last Year"] == NO_DATA:
    out["Projected Value Next Year"] = "Not enough data"

  else:
    next_value = out["Current Value"] * (avg_change/100 + 1)
    out["Projected Value Next Year"] = round(next_value, 1)

  return out

def pretty_print_dict(dc):
  """
  Pretty prints a given dictionary, formatted as it would be coded
  """
  pretty_print_dict_r(dc, "dict", 2)

def pretty_print_dict_r(dc, prevkey, indent):
  """
  Recursive helper function for pretty_print_dict
  """
  print((" " * (indent - 2)) + prevkey + ": {")
  for (key, val) in dc.items():
    if type(val) is dict:
      pretty_print_dict_r(val, key, indent + 2)
    else:
      print((" " * indent) + key + ": " + str(round_if_number(val, 2)) + ",")
  print((" " * (indent - 2)) + "},")

def get_dept_id(school_id):
  """
  Given a school id, returns the corresponding department id, for use in
  querying the employee position roster data
  """
  res = reqs.get(f'{SCHOOL_PROFILE_URL}SingleSchoolProfile?SchoolID={school_id}')
  return res.json()["FinanceID"]

def school_employees(school_id):
  """
  Returns a filter that will retrieve only employees at the provided school id
  """
  return { "Dept ID": [ get_dept_id(school_id) ] }

def combine_filters(*filters):
  """
  Combines multiple filter objects into one
  """
  out = {}
  for obj in filters:
    for key, val in obj.items():
      if key in out:
        out[key] += val
      else:
        out[key] = val
  return out

def get_name_from_id(id):
  df = pd.read_csv("data/ids-to-names.csv")
  return df.loc[df["SchoolID"] == id]["SchoolLongName"].iat[0]

# this formats all files the same way
# this was only needed for the 2014-2016 files and shouldn't be needed for 
# future years but I'm leaving it here (commented) just in case
# FIXME: re-format the names to match here so you can compare full names. 
"""
for file in EPR_CSV_LIST:
  df = pd.read_csv(f'data/{file}')
  #df.drop("Unnamed: 0", inplace=True, axis=1)
  df["Annual Salary"] = df["Annual Salary"].apply(lambda x: str(x).replace(",", ""))
  df["FTE Annual Salary"] = df["FTE Annual Salary"].apply(lambda x: str(x).replace(",", ""))
  df["Annual Benefit Cost"] = df["Annual Benefit Cost"].apply(lambda x: str(x).replace(",", ""))
  df.to_csv(f'data/{file}', index=False)
"""