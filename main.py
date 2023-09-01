import pandas as pd
import os
import re # regex
import requests as reqs
import random

from helpers import *
from constants import *


def salary_report(sy, filters):
  """
  Takes in a dataframe representing part of an employee position roster.
  Returns a dict containing some useful datapoints about that dataframe.
  """
  df = pd.read_csv(f"data/employeepositionroster_{sy}-06-30.csv")
  df = filter(df, filters)
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

def full_school_report(sy, filters, id):
  """
  Report on all salary info and some info on performance metrics

  This is pretty sloppy :/ oh well
  """
  main_filter = school_employees(id)

  df_exists = True
  df_in = pd.read_csv(f"data/employeepositionroster_{sy}-06-30.csv")
  if not (get_dept_id(id) in df_in["Dept ID"].unique()):
    df_exists = False

  prev_df_exists = True
  if sy == 2014:
    prev_df_exists = False
  else:
    prev_df = pd.read_csv(f"data/employeepositionroster_{sy-1}-06-30.csv")
    if not (get_dept_id(id) in prev_df["Dept ID"].unique()):
      prev_df_exists = False
  
  json_exists = True
  res = reqs.get(f"{SCHOOL_PROFILE_URL}SchoolProfileInformation?SchoolID={id}&SchoolYear={sy}")
  json = res.json()
  if len(json) < 1:
    json_exists = False

  df = filter(df_in, main_filter)

  #df["Annual Salary"] = df["Annual Salary"].astype(float)
  df = df.dropna()
  df = df.sort_values("Annual Salary", ascending=False)

  teachers = filter(df, TEACHERS)

  teacher_filter = combine_filters(main_filter, TEACHERS)

  if df_exists and prev_df_exists:
    main_turn_rate = get_turnover_rate(sy, main_filter)
    teacher_turn_rate = get_turnover_rate(sy, teacher_filter)

  out = {}
  if df_exists:
    out["Average Salary"] = round(df["Annual Salary"].mean(), 1)
    out["Highest Salary"] = to_float(df["Annual Salary"].iat[0])
    out["Lowest Salary"] = to_float(df["Annual Salary"].iat[-1])
    out["Average Teacher Salary"] = round(teachers["Annual Salary"].mean(), 1)
  else:
    out["Average Salary"] = NO_DATA
    out["Highest Salary"] = NO_DATA
    out["Lowest Salary"] = NO_DATA
    out["Average Teacher Salary"] = NO_DATA

  if df_exists and prev_df_exists:
    out["Job Turnover Rate"] = round(main_turn_rate * 100, 1)
    out["Teacher Turnover Rate"] = round(teacher_turn_rate * 100, 1)
  else:
    out["Job Turnover Rate"] = NO_DATA
    out["Teacher Turnover Rate"] = NO_DATA

  if json_exists:
    out["College Enrollment Rate"] = to_float(json[0]["College_Enrollment_Rate_School"])
    out["Graduation Rate"] = to_float(json[0]["Graduation_Rate_School"])
    #out["ISAT Composite Score Meets/Exceeds"] = to_float(json[0]["ISAT_CompositeMeetsExceeds_Mean"])
    #out["PSAE Composite Score Meets/Exceeds"] = to_float(json[0]["PSAE_CompositeMeetsExceeds_Mean"])
  else:
    out["College Enrollment Rate"] = NO_DATA
    out["Graduation Rate"] = NO_DATA
    #out["ISAT Composite Score Meets/Exceeds"] = NO_DATA
    #out["PSAE Composite Score Meets/Exceeds"] = NO_DATA

  # The ISAT and PSAE ones appear to be the same for every school every year
  # which is why they are commented out at the moment

  return out

def current_year_report(sy, filters, id):
  """
  Report on all salary info and some info on performance metrics

  This is pretty sloppy :/ oh well

  ignores the sy argument, but it's needed in order to have the correct
  function signature
  """
  main_filter = school_employees(id)

  df_exists = True
  df_in = pd.read_csv(f"data/employeepositionroster_{CURRENT_YEAR}-06-30.csv")
  if not (get_dept_id(id) in df_in["Dept ID"].unique()):
    df_exists = False

  prev_df_exists = True
  if sy == 2014:
    prev_df_exists = False
  else:
    prev_df = pd.read_csv(f"data/employeepositionroster_{CURRENT_YEAR-1}-06-30.csv")
    if not (get_dept_id(id) in prev_df["Dept ID"].unique()):
      prev_df_exists = False
  
  json_exists = True
  res = reqs.get(f"{SCHOOL_PROFILE_URL}SingleSchoolProfile?SchoolID={id}")
  json = res.json()
  if len(json) < 1:
    json_exists = False

  df = filter(df_in, main_filter)

  #df["Annual Salary"] = df["Annual Salary"].astype(float)
  df = df.dropna()
  df = df.sort_values("Annual Salary", ascending=False)

  teachers = filter(df, TEACHERS)

  teacher_filter = combine_filters(main_filter, TEACHERS)

  if df_exists and prev_df_exists:
    main_turn_rate = get_turnover_rate(sy, main_filter)
    teacher_turn_rate = get_turnover_rate(sy, teacher_filter)

  out = {}
  if df_exists:
    out["Average Salary"] = round(df["Annual Salary"].mean(), 1)
    out["Highest Salary"] = to_float(df["Annual Salary"].iat[0])
    out["Lowest Salary"] = to_float(df["Annual Salary"].iat[-1])
    out["Average Teacher Salary"] = round(teachers["Annual Salary"].mean(), 1)
  else:
    out["Average Salary"] = NO_DATA
    out["Highest Salary"] = NO_DATA
    out["Lowest Salary"] = NO_DATA
    out["Average Teacher Salary"] = NO_DATA

  if df_exists and prev_df_exists:
    out["Job Turnover Rate"] = round(main_turn_rate * 100, 1)
    out["Teacher Turnover Rate"] = round(teacher_turn_rate * 100, 1)
  else:
    out["Job Turnover Rate"] = NO_DATA
    out["Teacher Turnover Rate"] = NO_DATA

  if json_exists:
    out["Attendance Rate"] = to_float(json["AttendanceRateCurrentYear"])
    out["College Enrollment Rate"] = to_float(json["CollegeEnrollmentRate"])
    out["4 Year Graduation Rate"] = to_float(json["GraduationRate4Year"])
    debug(f'{id} - {json["GraduationRate4Year"]}')
    out["SAT Average"] = to_float(json["SATSchoolAverage"])
    #out["ISAT Composite Score Meets/Exceeds"] = to_float(json[0]["ISAT_CompositeMeetsExceeds_Mean"])
    #out["PSAE Composite Score Meets/Exceeds"] = to_float(json[0]["PSAE_CompositeMeetsExceeds_Mean"])
  else:
    out["Attendance Rate"] = NO_DATA
    out["College Enrollment Rate"] = NO_DATA
    out["4 Year Graduation Rate"] = NO_DATA
    out["SAT Average"] = NO_DATA
    #out["ISAT Composite Score Meets/Exceeds"] = NO_DATA
    #out["PSAE Composite Score Meets/Exceeds"] = NO_DATA

  # The ISAT and PSAE ones appear to be the same for every school every year
  # which is why they are commented out at the moment

  return out

def get_turnover_rate(sy, filters):
  """
  Returns the rate (as a fraction) of job turnovers from sy-1 to sy
  """
  if sy == 2014: return 0
  prev_year = pd.read_csv(f"data/employeepositionroster_{sy-1}-06-30.csv")
  prev_year = filter(prev_year, filters)
  this_year = pd.read_csv(f"data/employeepositionroster_{sy}-06-30.csv")
  this_year = filter(this_year, filters)

  def get_last(x):
    try:
      out = x.split(",")[0]
      return out.upper()
    except:
      return ""

  new_prev = pd.DataFrame()
  new_prev["Pos #"] = prev_year["Pos #"]
  new_prev["Last"] = prev_year["Name"].map(get_last)

  new_curr = pd.DataFrame()
  new_curr["Pos #"] = this_year["Pos #"]
  new_curr["Last"] = this_year["Name"].map(get_last)

  compare = new_prev.merge(new_curr, on=['Pos #', 'Last'], how="left", indicator="Exist")
  num_left = len(compare[compare["Exist"] == "left_only"])
  num_total = len(new_prev)

  if num_total == 0: return 1

  return (num_left / num_total)

def changed_since_last_year(sy, filters, posno):
  """
  Returns true if the last name of the person in the position number changed
  (I know it's a little lazy, but checking the whole name is really hard since
  they changed the name format a few times). The fact that this will return a
  false negative if the new staff member has the same last name isn't really
  an issue since that's pretty uncommon and we really only care about the total
  turnover rate, so a single inaccuracy won't hurt us that much

  Returns False otherwise, even if the position is new

  This will break if they ever change the format so it doesn't start with
  LAST, ...
  """
  if sy == 2014:
    return False # we don't have data for 2013, so we'll assume it didn't change
  df = pd.read_csv(f"data/employeepositionroster_{sy}-06-30.csv")
  df = filter(df, filters)
  df2 = pd.read_csv(f"data/employeepositionroster_{sy - 1}-06-30.csv")
  df2 = filter(df2, filters)
  if not (posno in df2["Pos #"].unique()):
    return False

  current = str(df.loc[df["Pos #"] == posno]["Name"].iat[0]).split(",")[0]
  prev = str(df2.loc[df2["Pos #"] == posno]["Name"].iat[0]).split(",")[0]

  return current != prev

def all_trends(dc):
  """
  Expects a dict where keys are stats and values are dicts where
  keys are dates and values are the value for that stat

  Analyzes trends in the given data, such as rates of change
  """
  out = {}
  for key, dc2 in dc.items():
    out[key] = trends(dc2)
  return out

def analyze(fn, filters, *args):
  return all_trends(flip_sort(all_years(fn, filters, *args)))

def search(name):
  """
  Intended for use on command line
  Finds a list of schools matching the name
  """
  res = reqs.get(f"{SCHOOL_PROFILE_URL}TypeaheadSchoolSearch?SearchValue={name}")
  json = res.json()
  if len(json) == 0:
    print("No schools found")
    return
  for entry in json:
    print(f"{entry['SchoolLongName']} ({entry['SchoolID']})")
  return

def main_func(id):
  pretty_print_dict(analyze(full_school_report, {}, id))

#main_func(609755)

def compare_schools(ids):
  """
  ** UNTESTED **

  The way I used of calculating correllation is a bit sloppy and doesn't
  necessarily correspond to an exact statistical correllation

  Compares multiple schools. Creates a dictionary saying which of the schools
  has the highest number in that category, and then returns a dictionary saying,
  for each stat, which stats there is a correlation to. In other words, if a
  school was the highest in a certain stat, what other stats was it the highest
  in?

  Also returns a dict full of inverse correlations -- if a school was highest in
  a certain stat, which other stats was it the lowest in?
  """
  dicts = {}
  for id in ids:
    dicts[id] = current_year_report(CURRENT_YEAR, {}, id)

  highests = {}
  lowests = {}
  for id, dc in dicts.items():
    for key, val in dc.items():
      if val == NO_DATA: continue
      if not (key in highests.keys()):
        highests[key] = (val, id)
        lowests[key] = (val, id)
      if float(val) > highests[key][0]:
        highests[key] = (val, id)
      if float(val) < lowests[key][0]:
        lowests[key] = (val, id)

  matches = {}
  matches_inverse = {}
  for key, val in highests.items():
    matches[key] = []
    matches_inverse[key] = []
    for key2, val2 in highests.items():
      if key == key2: continue
      if val[1] == val2[1]: matches[key].append(key2)
      
    for key2, val2 in lowests.items():
      if key == key2: continue
      if val[1] == val2[1]: matches_inverse[key].append(key2)
  
  for key, val in lowests.items():
    for key2, val2 in highests.items():
      if key == key2: continue
      if val[1] == val2[1]: matches_inverse[key].append(key2)

    for key2, val2 in lowests.items():
      if key == key2: continue
      if val[1] == val2[1]: matches[key].append(key2)
  
  return (matches, matches_inverse)

def run_comparisons(times):
  """
  ** UNTESTED **

  Runs a bunch of comparisons to measure correlations between different
  stats

  Warning: this function is slow. it seems to take about 5000ms (5s) per run
  This probably depends on the quality of your connection, mine was good but not
  amazing when I tested it
  """
  out = {}
  first = True

  for _ in range(times):

    print(f'runs done: {_}')

    ids = []
    while len(ids) < 4:
      id = random.choice(ALL_HS_IDS)
      if not (id in ids):
        ids.append(id)
    
    (matches, matches_inverse) = compare_schools(ids)
    
    for key, val in matches.items():
      if not (f'{key}_pos' in out.keys()):
        out[f'{key}_pos'] = {}
        out[f'{key}_neg'] = {}
      for ele in val:
        if ele in out[f'{key}_pos'].keys():
          out[f'{key}_pos'][ele] += (.5 / times)
        else:
          out[f'{key}_pos'][ele] = (.5 / times)
    
    for key, val in matches_inverse.items():
      if not (f'{key}_pos' in out.keys()):
        out[f'{key}_pos'] = {}
        out[f'{key}_neg'] = {}
      for ele in val:
        if ele in out[f'{key}_neg'].keys():
          out[f'{key}_neg'][ele] += (.5 / times)
        else:
          out[f'{key}_neg'][ele] = (.5 / times)
    
  return out

pretty_print_dict(run_comparisons(10))