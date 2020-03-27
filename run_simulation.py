import time

import requests
import json


user_url = 'http://0.0.0.0:8000/user/'
login_url = 'http://0.0.0.0:8000/login/'
init_url = 'http://0.0.0.0:8000/init_model/'
input_url = 'http://0.0.0.0:8000/input/'
output_url = 'http://0.0.0.0:8000/output/'

# replace with your superuser
data = {"username": "user@user.com",  # username = email
        "password": "user user88"}

resp = requests.post(login_url, data=data)

print(resp.content)

json_resp = resp.json()

token = json_resp['token']  # get validation token
header = {'Authorization': 'Token ' + token}  # set request header

file = {'idf_file': ('a.idf', open('test_setup_files/a.idf', 'rb')),
        'epw_file': ('a.epw', open('test_setup_files/a.epw', 'rb'))}

init_data = {'model_name': 'sim88',
             'step_size': 600,
             'final_time': 24.0}

resp = requests.post(init_url, headers=header, data=init_data, files=file)

print(resp.text)

header = {'Authorization': 'Token ' + token}  # set request header
i = 0
shade = 1.0

while i <= 86400:
    input_dict = {'time_step': i, 'yShadeFMU': shade}

    input_data = {
        'fmu_model': 'sim88',
        'time_step': i,
        'input': json.dumps(input_dict)
    }

    resp = requests.post(input_url, headers=header, data=input_data)

    print(resp.text)

    i += 600
    time.sleep(1)