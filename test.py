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

idf_file = open(idf_file_path, 'rb')
epw_file = open(epw_file_path, 'rb')

# place .idf and .epw in simapi-python/test_setup_files/  replace a.idf and a.epw
file = {'idf_file': ('update.idf', idf_file),
        'epw_file': ('update.epw', epw_file)}

# model initialization parameters
init_data = {
    'model_name': initial_model_name,   # change name each time script is run!
    'container_id': None,
    'model_count': model_count,
    'step_size': 600,   # step size in seconds. 600 secs = 10 mins
    'final_time': 24.0  # 24 hours = 86400 secs
}

resp = requests.post(setup_user.init_url, headers=header, data=init_data, files=file)

# prints init_data on successful post
print(resp.text)
