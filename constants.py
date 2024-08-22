import pandas as pd
import os
import re # regex
import requests as reqs
import random

CURRENT_YEAR = 2024 # update this to be the latest year in the data folder

SCHOOL_PROFILE_URL = "https://api.cps.edu/schoolprofile/CPS/"

NO_DATA = "Not found"

#List of all employee position roster csv files
EPR_CSV_LIST = filter(lambda x: x.startswith("employeepositionroster"), os.listdir("data"))

ALL_IDS = pd.read_csv("data/ids-to-names.csv")["School_ID"].values.tolist()
ALL_HS_IDS = pd.read_csv("data/ids-to-names-hs.csv")["School_ID"].values.tolist()

DEBUG = False

# Filters
TEACHERS = { "Job Title": [ "Regular Teacher" ] }
PRINCIPALS = { "Job Title": [ "Principal" ] }