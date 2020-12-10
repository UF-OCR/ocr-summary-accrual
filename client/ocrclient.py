import requests
from requests.auth import HTTPBasicAuth
import os
import json

soap_client = os.environ.get('soap_client', None)


# Makes an API call to OnCore that checks to see if a valid Protocol Number has been provided
# The API call also checks to see if the Username provivded has access to the Protocol
# The function returns a Status Code and Content
# Content is a String variable that consists of 'accrual_info_only', 'protocol_no', and 'title'
def validate_protocol(username, password, protocol_no):
    protocol_request = os.environ.get('soap_client', None) + "validateProtocol/" + protocol_no
    response = requests.get(protocol_request, auth=HTTPBasicAuth(username, password), verify= False)
    return response.status_code, response.content

# Makes an API call to OnCore that POSTS the Summary Accrual information parsed from the Excel document as JSON
# Returns a status_code and content of the message that alerts the program if the POST was successful/unsuccessful
def post_accruals(data):
    accrual_request = os.environ.get('soap_client', None) + "accruals"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(accrual_request, data=json.dumps(data), headers=headers,verify= False)
    return response.status_code, response.content
