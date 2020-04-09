import json
import sys

import polling2
import requests

from setup import Setup

initial_model_name = sys.argv[1]
simulation_count = int(sys.argv[2])


def test_method(query, url):
    resp = requests.get(url=url, json={'query': query})
    json_data = resp.json()['data']['outputs']

    return len(json_data)


setup_user = Setup()
header = setup_user.login()

# query for all models in db related to initial_model_name.
model_query = """
           {{
               fmuModels(modelN: "{0}"){{
                    modelName
                }}
           }}
           """.format(initial_model_name)

d = requests.get(url=setup_user.graphql_url, json={'query': model_query}).json()['data']['fmuModels']

polling2.poll(
    lambda: len(requests.get(url=setup_user.graphql_url,
                             json={'query': model_query}).json()['data']['fmuModels']) == simulation_count,
    step=2,
    poll_forever=True)

r = requests.get(url=setup_user.graphql_url, json={'query': model_query})

i = 0
sim_names = []

while i < simulation_count:
    name = r.json()['data']['fmuModels'][i]['modelName']  # extract model name from graphql query response
    print(name)
    sim_names.append(name)  # store extracted model names.
    i += 1

shade = 1.0  # input value. Stays same on each iteration.

# up to 25 concurrent models can receive as input val(shade). [shade] * 25 expands the list from 1 to 25.
input_list = [shade] * simulation_count

i = 0  # first step
# run 24 hour (86400sec) simulation at 10 minute (600sec) time steps
while i < 86400:  # outer loop iterates over time steps

    j = 0
    while j < simulation_count:  # inner loop iterates over models, posing input to a different model on each iteration.
        input_dict = {'time_step': i, 'yShadeFMU': shade}  # input is user defined, can be any number of inputs

        input_data = {
            'fmu_model': sim_names[j],
            'time_step': i,
            'input_json': json.dumps(input_dict)
        }

        r = requests.post(setup_user.input_url, headers=header, data=input_data)
        print(r.text + ' ' + str(r.status_code))

        output_query = """
        {{
            outputs(modelN: "{0}", tStep: {1}) {{
                outputJson
            }}
        }}
        """.format(sim_names[j], i)

        # move outside loop and poll once for len() = n, where n is number of simulations!
        polling2.poll(
            lambda: test_method(query=output_query, url=setup_user.graphql_url) == 1,
            step=0.1,
            poll_forever=True)

        json_output = requests.get(url=setup_user.graphql_url, json={'query': output_query}).json()['data']['outputs']
        test = json.loads(json_output[0]['outputJson'])
        print("Output: " + str(test))
        print('\n')
        j += 1

    i += 600
