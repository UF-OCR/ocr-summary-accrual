import sys
import numpy as np
import pandas as pd


# Takes in data from the Excel document and the Mapping Sheets. Both are represented as two dimensional arrays
def excluded_rows(received_data, gender_data, ethnicity_data, race_data, disease_site_data):

    # cols = first row of the Excel document
    cols = received_data[0]

    # Runs if there is no data in the first row of the Excel document
    if cols is None:
        return None, None, None, None, "Empty data received"

    row_starts = 2

    # Runs if the user has not removed the Description section of the template
    if received_data[1][0] == "Description":
        row_starts = 4
        received_data = received_data[3:]
    # Runs if the user has removed the Description section of the template
    else:
        received_data = received_data[1:]

    # Runs if the only data in the Excel document is the Column headers
    if received_data is None:
        return None, None, None, None, "Empty rows received"

    # DataFrame where The first row of the Excel document sets the columns and the received_data is formatted into the correct column
    data = pd.DataFrame(data=received_data, columns=cols)

    # Replaces all whitespace characters from start to end of the line with the 'Not a Number' Numpy datatype
    data = data.replace(r'^\s*$', np.nan, regex=True)

    # Drops rows where all of the columns are empty
    data = data.dropna(how='all')

    # Rename the On Study Date* column to On Study Date
    data = data.rename(columns={"On Study Date*": "On Study Date"})

    # Set the cols value to a list version of the DataFrame columns value
    cols = list(data.columns)

    data['empty_onstudy'] = False
    data['invalid_age'] = False
    data['invalid_zip'] = False
    data['modified_rows'] = False

    # Runs if the id is not present in data
    if 'id' not in data:
        # Sets the data id value to equal the
        data['id'] = row_starts + np.arange(len(data))

    # Runs if the Gender column is not present in the Excel document
    if 'Gender' not in data:
        data['Gender'] = ''
    # Runs if the Gender column is present in the Excel document
    else:

        # Fills all empty Gender values with "No Value received"
        data['Gender'] = data['Gender'].fillna("No value received")

        # Formats all Gender values to be the String equivalent
        data['Gender'] = data['Gender'].apply(str)

        # Applies Regex on all Gender values.
        # The regex looks for the following pattern < Optional: '+' or '-' >< any one character >< all numbers between '0'and '9' >
        # Replaces the found patterns with ''
        data['Gender'] = data['Gender'].str.replace(r'[-+]?\.[0-9]*', '')

        # Runs if the Gender Sheet is present in the Excel document
        if gender_data is not None:

            # Creates a Dataframe of the Gender Sheet in the Excel Document
            gender_data = pd.DataFrame(data=gender_data[1:])

            # Creates a dictionary that will be used to map the Mapped Value to the OnCore Value
            gender_data_dict = createDict(gender_data)

            # Add an entry to map 'No value received' to the value 'No value received'
            gender_data_dict['No value received'] = 'No value received'

            # Removes leading and trailing whitespaces from the Gender values
            data['Gender'] = data['Gender'].str.strip()

            # Use the dictionary to set the correct OnCore Value from the Mapped Value
            data['Gender'] = data['Gender'].map(gender_data_dict)

            # Fills all Gender values that didn't have a mapped value with "No mapping found"
            data['Gender'] = data['Gender'].fillna("No mapping found")

    # Runs if the Ethnicity column is not present in the Excel document
    if 'Ethnicity' not in data:
        data['Ethnicity'] = ''
    # Runs if the Ethnicity column is present in the Excel document
    else:

        # Fills all empty Ethnicity values with "No Value received"
        data['Ethnicity'] = data['Ethnicity'].fillna("No value received")

        # Formats all Ethnicity values to be the String equivalent
        data['Ethnicity'] = data['Ethnicity'].apply(str)

        # Applies Regex on all Gender values.
        # The regex looks for the following pattern < Optional: '+' or '-' >< any one character >< all numbers between '0'and '9' >
        # Replaces the found patterns with ''
        data['Ethnicity'] = data['Ethnicity'].str.replace(r'[-+]?\.[0-9]*', '')

        # Runs if the Ethnicity Sheet is present in the Excel document
        if ethnicity_data is not None:

            # Creates a Dataframe of the Ethnicity Sheet in the Excel Document
            ethnicity_data = pd.DataFrame(data=ethnicity_data[1:])

            # Creates a dictionary that will be used to map the Mapped Value to the OnCore Value
            ethnicity_data_dict = createDict(ethnicity_data)

            # Add an entry to map 'No value received' to the value 'No value received'
            ethnicity_data_dict['No value received'] = 'No value received'

            # Removes leading and trailing whitespaces from the Ethnicity values
            data['Ethnicity'] = data['Ethnicity'].str.strip()

            # Use the dictionary to set the correct OnCore Value from the Mapped Value
            data['Ethnicity'] = data['Ethnicity'].map(ethnicity_data_dict)

            # Fills all Ethnicity values that didn't have a mapped value with "No mapping found"
            data['Ethnicity'] = data['Ethnicity'].fillna("No mapping found")

    # Runs if the Race column is not present in the Excel document
    if 'Race' not in data:
        data['Race'] = ''
    # Runs if the Race column is present in the Excel document
    else:

        # Fills all empty Race values with "No Value received"
        data['Race'] = data['Race'].fillna("No value received")

        # Formats all Race values to be the String equivalent
        data['Race'] = data['Race'].apply(str)

        # Applies Regex on all Gender values.
        # The regex looks for the following pattern < Optional: '+' or '-' >< any one character >< all numbers between '0'and '9' >
        # Replaces the found patterns with ''
        data['Race'] = data['Race'].str.replace(r'[-+]?\.[0-9]*', '')

        # Runs if the Race Sheet is present in the Excel document
        if race_data is not None:

            # Creates a Dataframe of the Race Sheet in the Excel Document
            race_data = pd.DataFrame(data=race_data[1:])

            # Creates a dictionary that will be used to map the Mapped Value to the OnCore Value
            race_data_dict = createDict(race_data)

            # Add an entry to map 'No value received' to the value 'No value received'
            race_data_dict['No value received'] = 'No value received'

            # Removes leading and trailing whitespaces from the Race values
            data['Race'] = data['Race'].str.strip()

            # Use the dictionary to set the correct OnCore Value from the Mapped Value
            data['Race'] = data['Race'].map(race_data_dict)

            # Fills all Race values that didn't have a mapped value with "No mapping found"
            data['Race'] = data['Race'].fillna("No mapping found")

    # Runs if the Disease Site column is not present in the Excel document
    if 'Disease Site' not in data:
        data['Disease Site'] = ''
    # Runs if the Disease Sit column is present in the Excel document
    else:
        # Fills all empty Disease Site values with "No Value received"
        data['Disease Site'] = data['Disease Site'].fillna("No value received")

        # Runs if the Disease Site Sheet is present in the Excel document
        if disease_site_data is not None:

            # Creates a Dataframe of the Disease Site Sheet in the Excel Document
            disease_site_data = pd.DataFrame(data=disease_site_data[1:])

            # Creates a dictionary that will be used to map the Mapped Value to the OnCore Value
            disease_site_data_dict = createDict(disease_site_data)

            # Add an entry to map 'No value received' to the value 'No value received'
            disease_site_data_dict['No value received'] = "No value received"

            # Removes leading and trailing whitespaces from the Disease Site values
            data['Disease Site'] = data['Disease Site'].str.strip()

            # Use the dictionary to set the correct OnCore Value from the Mapped Value
            data['Disease Site'] = data['Disease Site'].map(disease_site_data_dict)

            # Fills all Disease Site values that didn't have a mapped value with "No mapping found"
            data['Disease Site'] = data['Disease Site'].fillna("No mapping found")

    try:
        # Runs if the Date of Birth column is present in the Excel document
        if 'Date of Birth' in data:

            # Formats all Date of Birth values to be the Datetime equivalent
            data['Date of Birth'] = pd.to_datetime(data['Date of Birth'])

            # Formats all Date of Birth values to the format yyyy-mm-dd
            data['Date of Birth'] = data['Date of Birth'].dt.strftime('%Y-%m-%d')
    except:
        return None, None, None, None, "Something went wrong while processing the date of birth field"

    try:
        # Runs if the On Study Date column is present in the Excel document
        if 'On Study Date' in data:

            # Gets an array of all of the indexes where the On Study Date is equal to NaN
            on_study_date_missing_rows = data[data['On Study Date'].isna() == True].index

            # Sets the data['empty_onstudy'] value to true. This lets the program know that there are rows with missing On Study Date values
            data.loc[on_study_date_missing_rows, ['empty_onstudy']] =  True

            # Formats all On Study Date values to be the Datetime equivalent
            data['On Study Date'] = pd.to_datetime(data['On Study Date'])

            # Formats all On Study Date values to the format yyyy-mm-dd
            data['On Study Date'] = data['On Study Date'].dt.strftime('%Y-%m-%d')
    except:
        return None, None, None, None, "Something went wrong while processing the on study date field"

    try:
        # Runs if the Zip Code column is present in the Excel document
        if 'Zip Code' in data:

            # Gets the number of rows where the Zip Code Value is missing
            zip_code_na_len = len(data[data['Zip Code'].isna()].index)

            # Gets the number of rows
            zip_code_len = len(data['Zip Code'].index)

            if zip_code_na_len != zip_code_len:

                # The Regex pattern starts at the beginning of the line. Matches any character except line breaks. Matches between 1 and 15 characters.
                zipcode_exp = '^.{1,15}$'

                # Formats all Zip Code values to be the String equivalent
                data['Zip Code'] = data['Zip Code'].apply(str)

                # Replaces all empty Zip Code values with the value NaN
                data['Zip Code'] = data['Zip Code'].replace("", np.nan)

                # Replaces all Zip Code values equal to 'nan' with the value NaN
                data['Zip Code'] = data['Zip Code'].replace("nan", np.nan)

                # Gets an array of all of the indexes where the Zip Code has a pattern that matches the zipcode_exp Regex
                numeric_index = data[data['Zip Code'].str.contains(str(zipcode_exp), na=True, regex=True) == False].index

                # Sets the data['invalid_zip'] value to true. This lets the program know that there are rows with invalid Zip Code values
                data.loc[numeric_index, ['invalid_zip']] = True

                # Fills all empty Zip Code values with "No Value received"
                data['Zip Code'] = data['Zip Code'].fillna("No value received")
    except:
        return None, None, None, None, "Something went wrong while processing the zip code field"
    try:
        # Runs if the Age at Enrollment column is present in the Excel document
        if 'Age at Enrollment' in data:

            # Gets the number of rows where the Age Value is missing
            age_na_len = len(data[data['Age at Enrollment'].isna()].index)

            # Gets the number of rows
            age_len = len(data['Age at Enrollment'].index)

            if age_na_len != age_len:

                # The Regex pattern starts at the beginning of the line. Matches the following age ranges:
                # 0-9, 10-89, 90-99, 100-129, 130-135
                age_range_exp = '^([0-9]|[1-8][0-9]|9[0-9]|1[0-2][0-9]|13[0-5])$'

                # Formats all Age at Enrollment values to be the Datetime equivalent
                data['Age at Enrollment'] = data['Age at Enrollment'].astype(str)

                # The regex looks for the following pattern < Optional: '+' or '-' >< any one character >< all numbers between '0'and '9' >
                # Replaces the found patterns with ''
                data['Age at Enrollment'] = data['Age at Enrollment'].str.replace(r'[-+]?\.[0-9]*', '')

                # Replaces all empty Age at Enrollment values with the value NaN
                data['Age at Enrollment'] = data['Age at Enrollment'].replace("", np.nan)

                # Replaces all Age at Enrollment values equal to 'nan' with the value NaN
                data['Age at Enrollment'] = data['Age at Enrollment'].replace("nan", np.nan)

                # Gets an array of all of the indexes where the Age at Enrollment has a pattern that matches the age_range_exp Regex
                numeric_index = data[data['Age at Enrollment'].str.contains(str(age_range_exp), na=True, regex=True)==False].index

                data.loc[numeric_index, ['invalid_age']] = True
                data['Age at Enrollment'] = data['Age at Enrollment'].fillna("No value received")
    except:
        return None, None, None, None, "Something went wrong while processing the age at enrollment field"

    modified_rows = data[(data['Gender'] == "No mapping found") | (data['Ethnicity'] == "No mapping found") | (data['Race'] == "No mapping found") | (data['Disease Site'] == "No mapping found")].index

    data.loc[modified_rows, ['modified_rows']] = True

    data = data.fillna("No value received")

    missing_rows = len(data[(data['invalid_age']) | (data['empty_onstudy']) | (data['invalid_zip'])].index)
    modified_rows = len(data[(data['invalid_age'] == False) & (data['empty_onstudy'] == False) & (data['invalid_zip'] == False) & (data['modified_rows'])].index)

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
