import sys
import numpy as np
import pandas as pd

def excluded_rows(received_data, gender_data, ethnicity_data, race_data, disease_site_data):
    cols = received_data[0]

    if cols is None:
        return None, None, None, None, "Empty data received"
    row_starts = 2
    if received_data[1][0] == "Description":
        row_starts = 4
        received_data = received_data[3:]
    else:
        received_data = received_data[1:]

    if received_data is None:
        return None, None, None, None, "Empty rows received"

    data = pd.DataFrame(data=received_data, columns=cols)
    data = data.replace(r'^\s*$', np.nan, regex=True)
    data = data.dropna(how='all')
    data = data.rename(columns={"On Study Date*": "On Study Date"})

    cols = list(data.columns)

    data['empty_onstudy'] = False
    data['invalid_age'] = False
    data['invalid_zip'] = False
    data['modified_rows'] = False

    if 'id' not in data:
        data['id'] = row_starts + np.arange(len(data))

    if 'Gender' not in data:
        data['Gender'] = ''
    else:
        data['Gender'] = data['Gender'].fillna("No value received")
        data['Gender'] = data['Gender'].astype(str)
        data['Gender'] = data['Gender'].str.replace(r'[-+]?\.[0-9]*', '')
        if gender_data is not None:
            gender_data = pd.DataFrame(data=gender_data[1:])
            gender_data_dict = createDict(gender_data)
            gender_data_dict['No value received'] = 'No value received'
            data['Gender'] = data['Gender'].map(gender_data_dict)
            data['Gender'] = data['Gender'].fillna("No mapping found")

    if 'Ethnicity' not in data:
        data['Ethnicity'] = ''
    else:
        data['Ethnicity'] = data['Ethnicity'].fillna("No value received")
        data['Ethnicity'] = data['Ethnicity'].astype(str)
        data['Ethnicity'] = data['Ethnicity'].str.replace(r'[-+]?\.[0-9]*', '')
        if ethnicity_data is not None:
            ethnicity_data = pd.DataFrame(data=ethnicity_data[1:])
            ethnicity_data_dict = createDict(ethnicity_data)
            ethnicity_data_dict['No value received'] = 'No value received'
            data['Ethnicity'] = data['Ethnicity'].map(ethnicity_data_dict)
            data['Ethnicity'] = data['Ethnicity'].fillna("No mapping found")

    if 'Race' not in data:
        data['Race'] = ''
    else:
        data['Race'] = data['Race'].fillna("No value received")
        data['Race'] = data['Race'].astype(str)
        data['Race'] = data['Race'].str.replace(r'[-+]?\.[0-9]*', '')
        if race_data is not None:
            race_data = pd.DataFrame(data=race_data[1:])
            race_data_dict = createDict(race_data)
            race_data_dict['No value received'] = 'No value received'
            data['Race'] = data['Race'].map(race_data_dict)
            data['Race'] = data['Race'].fillna("No mapping found")

    if 'Disease Site' not in data:
        data['Disease Site'] = ''
    else:
        data['Disease Site'] = data['Disease Site'].fillna("No value received")
        if disease_site_data is not None:
            disease_site_data = pd.DataFrame(data=disease_site_data[1:])
            disease_site_data_dict = createDict(disease_site_data)
            disease_site_data_dict['No value received'] = "No value received"
            data['Disease Site'] = data['Disease Site'].map(disease_site_data_dict)
            data['Disease Site'] = data['Disease Site'].fillna("No mapping found")

    try:
        if 'Date of Birth' in data:
            data['Date of Birth'] = pd.to_datetime(data['Date of Birth'])
            data['Date of Birth'] = data['Date of Birth'].dt.strftime('%Y-%m-%d')
    except:
        return None, None, None, None, "Something went wrong while processing the date of birth field"

    try:
        if 'On Study Date' in data:
            on_study_date_missing_rows = data[data['On Study Date'].isna() == True].index
            data.loc[on_study_date_missing_rows, ['empty_onstudy']] =  True
            data['On Study Date'] = pd.to_datetime(data['On Study Date'])
            data['On Study Date'] = data['On Study Date'].dt.strftime('%Y-%m-%d')
    except:
        return None, None, None, None, "Something went wrong while processing the on study date field"

    try:
        if 'Zip Code' in data:
            zip_code_na_len = len(data[data['Zip Code'].isna()].index)
            zip_code_len = len(data['Zip Code'].index)
            if zip_code_na_len != zip_code_len:
                zipcode_exp = '^[0-9]{5}(?:-[0-9]{4})?$'
                data['Zip Code'] = data['Zip Code'].astype(str)
                data['Zip Code'] = data['Zip Code'].str.replace(r'[-+]?\.[0-9]*', '')
                data['Zip Code'] = data['Zip Code'].replace("", np.nan)
                data['Zip Code'] = data['Zip Code'].replace("nan", np.nan)
                numeric_index = data[data['Zip Code'].str.contains(str(zipcode_exp), na=True, regex=True) == False].index
                data.loc[numeric_index, ['invalid_zip']] = True
                data['Zip Code'] = data['Zip Code'].fillna("No value received")
    except:
        return None, None, None, None, "Something went wrong while processing the zip code field"
    try:
        if 'Age at Enrollment' in data:
            age_na_len = len(data[data['Age at Enrollment'].isna()].index)
            age_len = len(data['Age at Enrollment'].index)
            if age_na_len != age_len:
                age_range_exp = '^([0-9]|[1-8][0-9]|9[0-9]|1[0-2][0-9]|13[0-5])$'
                data['Age at Enrollment'] = data['Age at Enrollment'].astype(str)
                data['Age at Enrollment'] = data['Age at Enrollment'].str.replace(r'[-+]?\.[0-9]*', '')
                data['Age at Enrollment'] = data['Age at Enrollment'].replace("", np.nan)
                data['Age at Enrollment'] = data['Age at Enrollment'].replace("nan", np.nan)
                numeric_index = data[data['Age at Enrollment'].str.contains(str(age_range_exp), na=True, regex=True)==False].index
                data.loc[numeric_index, ['invalid_age']] = True
                data['Age at Enrollment'] = data['Age at Enrollment'].fillna("No value received")
    except:
        return None, None, None, None, "Something went wrong while processing the age at enrollment field"

    modified_rows = data[(data['Gender'] == "No mapping found") | (data['Ethnicity'] == "No mapping found") | (data['Race'] == "No mapping found") | (data['Disease Site'] == "No mapping found")].index

    data.loc[modified_rows, ['modified_rows']] = True

    data = data.fillna("No value received")

    missing_rows = len(data[(data['invalid_age']) | (data['empty_onstudy'])].index)
    modified_rows = len(data[(data['invalid_age'] == False) & (data['empty_onstudy'] == False) & (data['modified_rows'])].index)

    data = data.sort_values(by=['id'], ascending=[True])

    return modified_rows, missing_rows, cols, data.to_dict(orient="index"), None

def accrual_summary(data):
    try:
        data = pd.DataFrame.from_dict(data, orient='index')
        data = data.replace(r'^\s+$', np.nan, regex=True)
        data = data.replace('', np.nan)
        data = data.dropna(how='all')
        drop_index = data[(data['invalid_age']) | (data['empty_onstudy']) | (data['invalid_zip'])].index
        if len(drop_index) > 0:
            data = data.drop(drop_index)

        data = data.replace("No value received","")
        data = data.replace("No mapping found", "")
        data = data.fillna("")

        total_accruals = len(data['On Study Date'])

        data = data.drop(columns=['empty_onstudy','invalid_age','modified_rows'])

        return total_accruals, data.to_json(orient="records")
    except:
        return -1, str(sys.exc_info()[1])


def createDict(data):
    data = data.fillna("")
    data = data.to_dict('splits')
    data = data["data"]
    data_dict = {}
    for i in data:
        data_dict[i[1]] = i[0]
    return data_dict
