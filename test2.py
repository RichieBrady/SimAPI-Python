import sys

import requests

from setup import Setup

initial_model_name = sys.argv[1]
model_count = sys.argv[2]

idf_file_path = 'test_setup_files/update.idf'
epw_file_path = 'test_setup_files/update.epw'

setup_user = Setup()

resp = setup_user.create_user()

print(resp.text + ' ' + str(resp.status_code))


header = setup_user.login()
print(model_count)
# model initialization parameters
init_data = {
    'model_name': initial_model_name,   # change name each time script is run!
    'container_id': None,
    'model_count': model_count,
    'step_size': 600,   # step size in seconds. 600 secs = 10 mins
    'final_time': 24.0  # 24 hours = 86400 secs
}

resp = requests.post(setup_user.send_fmu, headers=header, json=init_data)

# prints init_data on successful post
print(resp.text)
