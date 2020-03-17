## Introduction

Summary Accrual Import Tool is developed and maintained by the OnCore team in the Office of Clinical Research. The import tool allows study teams to upload a file with study enrollments and subsequently import those enrollments in OnCore as summary accruals. This summary accrual import process only applies to studies that are eligible to record summary data (see Study Eligibility below). 

### Study Eligibility: 

The study does not have clinical services occurring in a UF Health location (e.g. blood draws, labs, EKG’s). 

The study will not use an OnCore calendar. 

## Features: 

``IMPORTANT NOTE: During the import process, the import portal tool automatically removes all previously entered summary accrual entries for your study. This means that you should upload your entire list of enrolled subjects with each import.`` 

- Upload File:  The import tool allows users to upload summary accrual enrollments using an Excel file template provided by the Office of Clinical Research. Please find the details on the file in the Preparing Your File section. 

- User Authentication: The import tool uses the submitting user’s OnCore credentials to validate access to the given protocol. 

- Data Review: After submission of the Excel file and successful authentication, the import tool parses through the data and generates the summary accrual data which is displayed on the screen for the user to review. 

- Data Import:  After verifying the data to be imported, user can import the data into OnCore via import button 

## Preparing Your File:  

To prepare your file use the excel template provided by Office of Clinical Research. The import template allows you to add accrual data including one or more of the following attributes: 

- On Study Date (required) 

- Institution, Gender 

- Date of Birth 

- Age at Enrollment 

- Ethnicity 

- Race 

- Disease site 

- Diagnosis 

- Recruited By (Last Name, First Name) 

- Recruited Institution 

- Participant Zip Code 

- Page Break
 

## Data Mapping: 

When importing accruals that include Gender, Race, Ethnicity, or Disease Site (oncology only), the values in your dataset should match the default OnCore system values. If the option lists in your dataset are different from the OnCore system values, you can map them to the OnCore values using the four mapping sheets in the Excel template: 

- Gender  

- Ethnicity 

- Race 

- Disease Site 

``Note:  If your dataset values are the same as the OnCore values, no changes to these mapping sheets need to be made. If any values in your dataset are not mapped, the import tool will ignore all data with those values. 
``
## Authentication: 

Before importing data into OnCore, the import tool asks the user for their OnCore credentials (e.g. Gatorlink login & password) which are used to verify their OnCore permissions. Import Tool users must have access to Summary Accrual entry in OnCore and must also have access to the study for which the accruals are being imported. Contact the OnCore Support team for questions about access permissions (oncore-support@ahc.ufl.eduu).  