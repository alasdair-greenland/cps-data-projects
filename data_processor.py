import pandas as pd
import os
import re # regex
import requests as reqs
import random

import numpy
import scipy

import matplotlib.pyplot as plt

from helpers import *
from constants import *

ISP = 0
NETWORK_SCHOOL = 1
NETWORK_OFFICE = 2
CENTRAL_OFFICE = 3
CHARTER = 4 # also includes contract schools

TEACHER_POSITIONS = [
    'Bilingual Teacher' ,
    'PartTime Teacher' ,
    'Regular Teacher' ,
    'School Counselor',
    'Special Education Teacher'
]

def format_name(n):
    n = n.strip()
    n = n.replace(' Miss ', ' ')
    n = n.replace(' Ms. ', ' ')
    n = n.replace(' Mr. ', ' ')
    n = n.replace(' Mrs. ', ' ')
    n = n.replace('.', '')
    n = n.replace('"', '')
    return n

dn = 0

# Finds the job (if there is one) in df that matches the one represented by row
# df is one of processed_data/position_data/YEAR.csv and row is a row from an 
# employeepositionroster.
# Since we don't have employee ids, "same job" is defined as the same name working in the
# same position at the same school.
# this is only run when populating processed_data/position_data, because we then assign
# "job ids" which make it possible to search for the same job across different years
def find_same_job(df, row):
    global dn
    if pd.isnull(row["Name"]): return None
    test_name = format_name(str(row["Name"]))
    def matches_row(newrow):
        """
        print(f"{str(newrow["Name"])}|")
        print(f"{format_name(str(row["Name"]))}|")
        print(f"{str(newrow["Job Title"])}|")
        print(f"{str(row["Job Title"])}|")
        print(f"{str(newrow["Dept ID"])}|")
        print(f"{str(row["Dept ID"])}|")
        print("\n")
        """
        return (
            str(newrow["Name"]) == test_name and 
            str(newrow["JobCode"]) == str(row["JobCode"]) and 
            str(newrow["Dept ID"]) == str(row["Dept ID"])
        )
    rows = df[df.apply(matches_row, axis=1)]
    if len(rows) > 0:
        return rows.iloc[0]
    else:
        return None

# creates position_data/YEAR.csv
# this should only ever be run on its own for the most recent year,
# because it needs to look at the equivalent file for the previous year
# if it is necessary to update previous years' data (i.e. to change formatting 
# or add fields), run make_all_position_data (which calls this)
# this function is very slow due to making over a billion
# lookups and checks - should take between one and two hours
def make_position_data(year):
    cols = [ 'Job ID', 'Pos #', 'JobCode', 'Job Title', 'Dept ID', 'Department', 'Salary', 'Raise', 'ExistedLastYear', 'Name' ]
    f = open(f'processed_data/position_data/{year}.csv', 'w')
    f.write(",".join(cols))
    f.write('\n')
    df = pd.read_csv(f'data/employeepositionroster_{year}-06-30.csv', encoding='latin-1')
    if year == 2014: # oldest year, no previous data
        cid = 1
        for index, row in df.iterrows():
            info = [
                cid,
                row["Pos #"],
                row["JobCode"],
                f"\"{row["Job Title"]}\"",
                row["Dept ID"],
                f"\"{row["Department"]}\"",
                row["Annual Salary"],
                -1,
                False,
                f"\"{format_name(str(row["Name"]))}\""
            ]
            if pd.isnull(row["Name"]):
                info[-1] = ""
                info[-4] = 0
            cid += 1
            info = list(map(str, info))
            f.write(",".join(info))
            f.write("\n")
    else:
        df2 = pd.read_csv(f'processed_data/position_data/{year-1}.csv', encoding='latin-1')
        # if this dataframe doesn't exist, it's because this function wasn't run
        # for the previous year
        cid = df2["Job ID"].max() + 1
        for index, row in df.iterrows():
            prev_row = find_same_job(df2, row)
            if prev_row is None:
                info = [
                    cid,
                    row["Pos #"],
                    row["JobCode"],
                    f"\"{row["Job Title"]}\"",
                    row["Dept ID"],
                    f"\"{row["Department"]}\"",
                    row["Annual Salary"],
                    -1,
                    False,
                    f"\"{format_name(str(row["Name"]))}\""
                ]
                if pd.isnull(row["Name"]):
                    info[-1] = ""
                    info[-4] = 0
                cid += 1
            else:
                info = [
                    prev_row["Job ID"],
                    prev_row["Pos #"],
                    prev_row["JobCode"],
                    f"\"{prev_row["Job Title"]}\"",
                    prev_row["Dept ID"],
                    f"\"{prev_row["Department"]}\"",
                    row["Annual Salary"],
                    row["Annual Salary"] - prev_row["Salary"],
                    True,
                    f"\"{prev_row["Name"]}\""
                ]
            info = list(map(str, info))
            f.write(",".join(info))
            f.write("\n")

# it should never be necessary to run this,
# unless updating all years' data to change formatting
def make_all_position_data():
    for year in range(2014, CURRENT_YEAR + 1):
        make_position_data(year)

# returns true iff the job title refers to a teaching job
def is_teaching_job(title):
    return title in [ 'Bilingual Teacher','PartTime Teacher','Regular Teacher','School Counselor','Special Education Teacher' ]

# populates processed_data/department_data/YEAR.csv with info about
# departments w.r.t. jobs/budget
def make_department_data(year):
    df = pd.read_csv(f"processed_data/position_data/{year}.csv", encoding="latin-1")
    df2 = pd.read_csv("data/network_data.csv", encoding="latin-1")
    out = {}
    cols = ["Dept ID", "Department", "Network", "Total Staff", "Teaching Staff", "Total Staff Budget", "Teaching Staff Budget", "Students", "Teacher Spending Per Student" ]
    for index, row in df.iterrows():
        did = row["Dept ID"]
        if did == 0: continue
        if not did in out:
            out[did] = [
                did,
                row["Department"],
                "",
                0,
                0,
                0,
                0,
                0,
                0
            ]
            newrows = df2.loc[df2["Dept ID"] == row["Dept ID"]]
            if not newrows.empty > 0:
                out[did][2] = newrows.iloc[0]["Network"]
                out[did][-2] = newrows.iloc[0]["Students"]
        out[did][3] += 1
        out[did][5] += row["Salary"]
        if is_teaching_job(row["Job Title"]):
            out[did][4] += 1
            out[did][6] += row["Salary"]
            if out[did][-2] > 0:
                out[did][-1] += row["Salary"] / out[did][-2]
                out[did][-1] = round(out[did][-1], 2)
    df_out = pd.DataFrame.from_dict(out, orient="index", columns=cols)
    df_out.to_csv(f"processed_data/department_data/{year}.csv")

# populates processed_data/network_data/YEAR.csv with info about
# networks w.r.t. department stats
# Note that this is administrative network, not geographic network
def make_department_network_data(year):
    df = pd.read_csv(f"processed_data/department_data/{year}.csv", encoding="latin-1")
    out = {}
    cols = [ "Total Schools", "Average Staff Budget", "Average Teacher Budget", "Average Teacher Budget Per Student" ]
    for index, row in df.iterrows():
        net = row["Network"]
        if not net in out:
            out[net] = [
                0,
                0,
                0,
                0
            ]
        out[net][0] += 1
        out[net][1] += row["Total Staff Budget"]
        out[net][2] += row["Teaching Staff Budget"]
        out[net][3] += row["Teacher Spending Per Student"]
    for key in out:
        r = out[key]
        r[1] = round(r[1] / r[0], 2)
        r[2] = round(r[2] / r[0], 2)
        r[3] = round(r[3] / r[0], 2)
    df_out = pd.DataFrame.from_dict(out, orient="index", columns=cols)
    df_out.to_csv(f"processed_data/network_data/{year}.csv")

# populates data/network_data.csv with various api info about schools
# this is done so that this is the only place api lookups need to happen
# takes a few minutes to run, depending on strength of network connection
def make_network_data():
    df = pd.read_csv("data/ids-to-names.csv")
    f = open("data/network_data.csv", "w")
    f.write("School ID,Dept ID,Network,Geographic Network,Students,Attendance Rate,ISAT Composite\n")
    for index, row in df.iterrows():
        sid = row["School_ID"]
        res = reqs.get(f'{SCHOOL_PROFILE_URL}SingleSchoolProfile?SchoolID={sid}')
        json = res.json()
        if type(json) == str:
            continue
        did = json["FinanceID"]
        net = json["Network"]
        ss = json["StatisticsSummary"]
        students = re.search(r"\d+", ss).group()
        gnet = json["GeographicNetwork"]
        att = json["AttendanceRateCurrentYear"]
        isat = json["ISATCompositeMeetsExceeds"]
        f.write(f"{sid},{did},{net},{gnet},{students},{att},{isat}\n")

# run this once data/employeepositionroster_YEAR-06-30.csv has been added
def make_new_year_data():
    year = CURRENT_YEAR
    make_position_data(year)
    make_network_data() # needs to be run because api fields will have changed
    make_department_data(year)
    make_department_network_data(year)