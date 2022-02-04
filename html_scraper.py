from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from os.path import exists

# SET DATES
drilling_report_file_name = 'drilling_reports\drilling_report_01-12-2022.htm'
report_date = '01/12/2022'
prev_week = '01/03/2022'  # '' if no file
prev_month = ''  # '' if no file

# READ PREVIOUS FILE
file_name_prev_week = prev_week[:2] + '-' + \
    prev_week[3:5] + '-' + prev_week[6:10]
prev_file_name = 'rig_lists/raw_rig_list_' + file_name_prev_week + '.csv'
if len(prev_week) != 0:  # Skips import if prev week is blank
    import_df = pd.read_csv(prev_file_name)
else:
    pass


def strip_tags(data):
    # FUNCTION FOR STRIPPING HTML TAGS
    i = 0
    for d in data:
        data[i] = d.get_text()
        i += 1


# -------------------------------------------------

with open(drilling_report_file_name) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

# GET COUNTIES
counties = soup.find_all('div', class_='chr--left')
strip_tags(counties)
# GET RIG COUNT BY COUNTY
raw_county_rig_count = soup.find_all('div', class_='chr--right')
strip_tags(raw_county_rig_count)
i = 0
rigs_per_county = []
for d in raw_county_rig_count:
    a = d.replace('Count: ', "").replace(' Total', "")
    rigs_per_county.append(a)
    i += 1

# CREATE DF FOR RIGCOUNT BY COUNTY
county_rig_count = pd.DataFrame(
    list(zip(counties, rigs_per_county)), columns=['county', 'rig_count'])
county_rig_count['rig_count'] = county_rig_count['rig_count'].astype('int')

# GET LIST OF OPERATORS
operators = []
operator_rows = soup.find_all('div', class_='operator-row')
i = 0
for a in operator_rows:
    b = a.find_all(class_='name')
    strip_tags(b)
    operators.append(b)

# CREATE OUTPUT DF WITH OPERATOR LIST COUNTIES WILL BE MERGED TO THIS
out_df = pd.DataFrame(operators, columns=['Operator'])

# MAKES A COUNTY LIST THAT CAN BE MERGED WITH OPERATOR LIST
out_county_list = []
for i, row in county_rig_count.iterrows():
    for j in range(row['rig_count']):
        out_county_list.append(row['county'])

# MERGE COUNTY LIST WITH OPERATOR LIST
county_list = pd.DataFrame(out_county_list, columns=['County'])
out_df = pd.concat([out_df, county_list], axis=1)
out_df['County'] = out_df['County'].str.replace(" County", "")


# GET DATA
well_data_values = soup.find_all('td', class_='detail-value')
strip_tags(well_data_values)

# INITIATE COLUMNS
drill_type = []
well = []
rig = []
well_type = []
field = []
formation = []
permit_depth = []
spud_date = []
API_UWI = []
lat_long = []
rated_hp = []
permit_approval_date = []

# PULL DATA FROM WELL_DATA_VALUES AND PUT IN COLUMN LISTS
i = 0
for a in range(len(out_df)):
    drill_type.append(well_data_values[i])
    i += 12

i = 1
for a in range(len(out_df)):
    well.append(well_data_values[i])
    i += 12

i = 2
for a in range(len(out_df)):
    rig.append(well_data_values[i])
    i += 12

i = 3
for a in range(len(out_df)):
    well_type.append(well_data_values[i])
    i += 12

i = 4
for a in range(len(out_df)):
    field.append(well_data_values[i])
    i += 12

i = 5
for a in range(len(out_df)):
    formation.append(well_data_values[i])
    i += 12

i = 6
for a in range(len(out_df)):
    permit_depth.append(well_data_values[i])
    i += 12

i = 7
for a in range(len(out_df)):
    spud_date.append(well_data_values[i])
    i += 12

i = 8
for a in range(len(out_df)):
    API_UWI.append(well_data_values[i])
    i += 12

i = 9
for a in range(len(out_df)):
    lat_long.append(well_data_values[i])
    i += 12

i = 10
for a in range(len(out_df)):
    rated_hp.append(well_data_values[i])
    i += 12

i = 11
for a in range(len(out_df)):
    permit_approval_date.append(well_data_values[i])
    i += 12


# MAKE LISTS DF COLUMNS AND FORMAT
out_df['report_date'] = report_date
out_df['drill_type'] = drill_type
out_df['drill_type'] = out_df['drill_type'].str.strip()
out_df['well'] = well
out_df['rig'] = rig
out_df['well_type'] = well_type
out_df['well_type'].str.strip()
out_df['field'] = field
out_df['formation'] = formation
out_df['permit_depth'] = permit_depth
out_df['spud_date'] = spud_date
out_df['API_UWI'] = API_UWI
out_df['lat_long'] = lat_long
out_df['rated_hp'] = rated_hp
out_df['permit_approval_date'] = permit_approval_date
out_df['state_id'] = out_df['API_UWI'].str[:2]
out_df['state_id'] = out_df['state_id'].str.strip().replace("", 0)
out_df['state_id'] = out_df['state_id'].astype('int64')
out_df['county_id'] = out_df['API_UWI'].str[3:6]
out_df['county_id'] = out_df['county_id'].str.strip().replace("", 0)
out_df['county_id'] = out_df['county_id'].astype('int64')

# ASSOCIATE STATE NAMES WITH API WELL NUMBER
states = ['AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN',
          'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
          'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
          'VA', 'WA', 'WV', 'WI', 'WY', 'AK', 'HI',
          'AK-OS', 'PO-OS', 'GOM', 'AO-OS', '']

state_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
              12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
              23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
              34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
              45, 46, 47, 48, 49, 50, 51,
              55, 56, 60, 61, 0]

state_id_df = pd.DataFrame(
    list(zip(states, state_nums)), columns=['state', 'state_id'])

# IMPORT LIST OF BASINS
basin_df = pd.read_csv('basin_list.csv')

# MERGE STATE AND BASINS WITH DF, REORDER COLUMNS
out_df = out_df.merge(state_id_df, how='left', on='state_id')
state_col = out_df.pop('state')
out_df.insert(1, 'State', state_col)
out_df = out_df.merge(basin_df, how='left', on=['State', 'County'])
basin_col = out_df.pop('Basin')
out_df.insert(0, 'Basin', basin_col)

# DEFINE OUTPUT FILENAME
file_name_report_date = report_date[:2] + '-' + \
    report_date[3:5] + '-' + report_date[6:10]
out_file_name = 'rig_lists/raw_rig_list_' + file_name_report_date + '.csv'

# IF IMPORTED FILE, MAKE THIS WEEK DF FOR ADD/DROP RIGS, ADD IMPORT
# MAKE LAST WEEK DF FOR ADD/DROP RIGS
if len(prev_week) != 0:
    this_week_df = out_df
    out_df = pd.concat([out_df, import_df])
    last_week_df = out_df[out_df['report_date'] == prev_week]
else:
    pass

# WRITE OUTPUT DF TO FILE
out_df.to_csv(out_file_name)

# -------------------------------------------------------------------------
# CREATES AGGREGATED DATA
# IF IMPORTED FILE, CREATES ADDED RIGS AND DROPPED RIGS LISTS
if len(prev_week) != 0:
    add_rig_file_name = 'add_drop_rigs/added_rigs_' + file_name_report_date + '.csv'
    drop_rig_file_name = 'add_drop_rigs/dropped_rigs_' + file_name_report_date + '.csv'
    added_rigs = pd.merge(last_week_df, this_week_df, on=['rig'], how="outer",
                          indicator=True).query('_merge=="right_only"')
    added_rigs.to_csv(add_rig_file_name)
    dropped_rigs = pd.merge(this_week_df, last_week_df, on=['rig'], how="outer",
                            indicator=True).query('_merge=="right_only"')
    dropped_rigs.to_csv(drop_rig_file_name)
    # CREATES RIG COUNT BY BASIN
    rig_count_by_basin = pd.crosstab(
        out_df["Basin"], out_df["report_date"], values=out_df["API_UWI"],
        margins=True, aggfunc='count')
    rig_count_by_basin.to_csv('basin_rig_count.csv')
    # CREATES RIG COUNT BY BASIN
    rig_count_by_operator = pd.crosstab(
        out_df["Operator"], out_df["report_date"], values=out_df["API_UWI"],
        margins=True, aggfunc='count')
    rig_count_by_operator.to_csv('operator_rig_count.csv')
    # CREATES RIG COUNT BY BASIN BY OPERATOR
    rig_count_by_basin_operator = pd.crosstab(
        [out_df["Basin"], out_df['Operator']], out_df["report_date"],
        values=out_df["API_UWI"], margins=True, aggfunc='count')
    rig_count_by_basin_operator.to_csv('basin_operator_rig_count.csv')
    # PRINT STATS
    print(import_df.shape[0])
    print(out_df.shape[0])
    print(added_rigs.shape[0])
    print(dropped_rigs.shape[0])
else:
    pass
