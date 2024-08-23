import pandas as pd

# Obselete at this point, just prefixes from names
def format_name(n):
    n = n.strip()
    n = n.replace(' Miss ', ' ')
    n = n.replace(' Ms. ', ' ')
    n = n.replace(' Mr. ', ' ')
    n = n.replace(' Mrs. ', ' ')
    n = n.replace('.', '')
    n = n.replace('"', '')
    return n

# Finds the job (if there is one) in df that matches the one represented by row
# df is one of processed_data/position_data/YEAR.csv and row is a row from an 
# employeepositionroster.
# Since we don't have employee ids, "same job" is defined as the same name working in the
# same position at the same school.
# this is only run when populating processed_data/position_data, because we then assign
# "job ids" which make it possible to search for the same job across different years
def find_same_job(df, row, dict={}):
    if pd.isnull(row["Name"]): return None
    test_name = format_name(str(row["Name"]))
    def matches_row(newrow):
        return (
            str(newrow["Name"]) == test_name and
            str(newrow["JobCode"]) == str(row["JobCode"])
        )
    did = row["Dept ID"]
    if not (did in dict):
        dict[did] = df[df["Dept ID"] == did]
    df2 = dict[did]
    rows = df2[df2.apply(matches_row, axis=1)]
    if len(rows) > 0:
        return rows.iloc[0]
    return None

# returns true iff the job title refers to a teaching job
def is_teaching_job(title):
    return title in [ 'Bilingual Teacher','PartTime Teacher','Regular Teacher','School Counselor','Special Education Teacher' ]

def calc_coefficient(row):
    if row["Teacher Spending Per Student"] == 0:
        return -1
    return row["Attendance Rate"] / row["Teacher Spending Per Student"]

# used to sort department data by various stats
# edit function to find the thing you're interested in
def stat_searcher():
    df = pd.read_csv("processed_data/department_data/2024.csv")
    for n in range(1, 18):
        str = f"NETWORK {n}"
        df_ = df[df["GeoNetwork"] == str]
        df_["Coefficient"] = df_.apply(calc_coefficient, axis=1)
        df_ = df_.sort_values("Coefficient", ascending=False)
        df_.to_csv(f"processed_data/network_{n}.csv")