import requests
from requests.auth import HTTPBasicAuth
import os
import json

soap_client = os.environ.get('soap_client', None)


def validate_protocol(username, password, protocol_no):
    protocol_request = os.environ.get('soap_client', None) + "validateProtocol/" + protocol_no
    response = requests.get(protocol_request, auth=HTTPBasicAuth(username, password), verify= False)
    return response.status_code, response.content


def post_accruals(data):
    accrual_request = os.environ.get('soap_client', None) + "accruals"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(accrual_request, data=json.dumps(data), headers=headers,verify= False)
    return response.status_code, response.content
