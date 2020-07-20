import json

import polling2
import requests
import pandas as pd


def send_and_generate(self, initial_model_name, model_count, step_size, final_time, idf_path, epw_path):
    resp = self.setup_user.create_user()

    print(resp.text + ' ' + str(resp.status_code))

    header = self.setup_user.login()

    idf_file = open(idf_path, 'rb')
    epw_file = open(epw_path, 'rb')

    # place .idf and .epw in simapi-python/data_files/  replace a.idf and a.epw
    file = {'idf_file': ('update.idf', idf_file),
            'epw_file': ('update.epw', epw_file)}

    # model initialization parameters
    init_data = {
        'model_name': initial_model_name,  # change name each time script is run!
        'container_id': None,
        'model_count': model_count,
        'step_size': step_size,  # step size in seconds. 600 secs = 10 mins
        'final_time': final_time  # 24 hours = 86400 secs
    }

    resp = requests.post(self.setup_user.init_url, headers=header, data=init_data, files=file)

    return resp.status_code


def send_and_init(self, initial_model_name, model_count, step_size, final_time, ):
    resp = self.setup_user.create_user()

    print(resp.text + ' ' + str(resp.status_code))

    header = self.setup_user.login()
    print(model_count)
    # model initialization parameters
    init_data = {
        'model_name': initial_model_name,  # change name each time script is run!
        'container_id': None,
        'model_count': model_count,
        'step_size': step_size,  # step size in seconds. 600 secs = 10 mins
        'final_time': final_time  # 24 hours = 86400 secs
    }

    resp = requests.post(self.setup_user.send_fmu, headers=header, json=init_data)

    # query for all models in db related to initial_model_name.
    model_query = """
                   {{
                      fmuModels(modelN: "{0}"){{
                         modelName
                      }}
                   }}
                   """.format(initial_model_name)

    r = requests.get(url=self.setup_user.graphql_url, json={'query': model_query}).json()['data']['fmuModels']

    self.initialized_model_count = len(r)
    # prints init_data on successful post
    return resp.status_code


def simulate_models(self, initial_model_name, model_count):
    def test_method(query, url):
        resp = requests.get(url=url, json={'query': query})
        json_data = resp.json()['data']['outputs']

        return len(json_data)

    header = self.setup_user.login()

    # query for all models in db related to initial_model_name.
    model_query = """
               {{
                   fmuModels(modelN: "{0}"){{
                        modelName
                    }}
               }}
               """.format(initial_model_name)

    r = requests.get(url=self.setup_user.graphql_url, json={'query': model_query})

    i = 0
    sim_names = []

    while i < model_count:
        name = r.json()['data']['fmuModels'][i]['modelName']  # extract model name from graphql query response
        print(name)
        sim_names.append(name)  # store extracted model names.
        i += 1

    f_time = 60 * 60 * int(self.f_time_text.get())
    step_size = int(self.t_step_text.get())

    data_frames = []
    for file in self.csv_paths:
        data_frames.append(pd.read_csv(file))

    i = 0  # first step
    while i < f_time:  # TODO Make final time generic

        j = 0
        # TODO process models async client side!
        while j < model_count:
            if len(data_frames) > 1:
                df = data_frames[j]
            else:
                df = data_frames[0]

            row = df.loc[df['time_step'] == i]
            input_dict = row.to_dict('records')
            input_dict = input_dict[0]
            input_data = {
                'fmu_model': sim_names[j],
                'time_step': i,
                'input_json': json.dumps(input_dict)
            }

            r = requests.post(self.setup_user.input_url, headers=header, data=input_data)
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
                lambda: test_method(query=output_query, url=self.setup_user.graphql_url) == 1,
                step=0.1,
                poll_forever=True)

            json_output = \
                requests.get(url=self.setup_user.graphql_url, json={'query': output_query}).json()['data'][
                    'outputs']

            test = json.loads(json_output[0]['outputJson'])
            print("Output: " + str(test) + "\n")
            j += 1

        i += step_size

    print("\nSimulation(s) finished!\n")
    return 200
