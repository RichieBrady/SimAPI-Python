import csv
import json
import logging
import polling2
import requests
import pandas as pd

user_url = 'http://0.0.0.0:8000/user/'
login_url = 'http://0.0.0.0:8000/login/'
init_url = 'http://0.0.0.0:8000/init_model/'
input_url = 'http://0.0.0.0:8000/input/'
output_url = 'http://0.0.0.0:8000/output/'
graphql_url = 'http://0.0.0.0:8000/graphql/'
send_fmu = 'http://0.0.0.0:8000/send_fmu/'


# TODO add utility method to prepare user csv e.g. add time step column etc.
class SimApi:

    def __init__(self, model_name, model_count, step_size, final_time, idf_path, epw_path, csv):
        """
        Class represents the programming interface exposed to a user of the SimApi system.
        :param model_name: (string) name of model must be unique
        :param model_count: (int) number of models to instantiate
        :param step_size: (int) size of each step per hour, value in seconds e.g. 4 steps per hour = 900 step size
        (15 minutes in seconds)
        :param final_time: (int) final runtime of model, value in hours. Will be changed to accommodate run times
        over a few days
        :param idf_path: (string) absolute path to .idf
        :param epw_path: (string) absolute path to .epw
        :param csv: (list) absolute path(s) to csv file(s), number of files must equal model count
        """
        self.logger = logging.getLogger('simapi')
        handler = logging.FileHandler('./simapi.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self._header = None
        self._model_name = model_name
        self._model_count = model_count
        self._step_size = step_size
        self._final_time = final_time
        self._idf_path = idf_path
        self._epw_path = epw_path
        self._csv = csv
        # model initialization parameters
        self._init_data = {
            'model_name': self._model_name,  # change name each time script is run!
            'container_id': None,
            'model_count': self._model_count,
            'step_size': self._step_size,  # step size in seconds. 600 secs = 10 mins
            'final_time': self._final_time  # 24 hours = 86400 secs
        }
        self.sim_names = []

    @staticmethod
    def create_user(user_email='user@user.com', user_name='user', user_password='user user88'):
        """
        Creates new user
        :param user_email: (string) user email
        :param user_name: (string) user name
        :param user_password: (string) user password
        :return:
        """
        # TODO add check for existing user
        json_data = {
            "name": user_name,
            "email": user_email,
            "password": user_password
        }

        return requests.post(user_url, data=json_data)

    def login(self, username="user@user.com", password="user user88"):
        """
        Login as current user and store user token as a header dictionary to be used in requests
        :param username: (string) user name
        :param password: (string) user password
        """
        data = {"username": username,  # username = email
                "password": password}

        resp = requests.post(login_url, data=data)

        if resp.status_code == 200:
            json_resp = resp.json()

            token = json_resp['token']  # get validation token
            self._header = {'Authorization': 'Token ' + token}  # set request header
        return resp.status_code

    def send_and_generate(self):
        """
        Send files needed to generate an fmu. return when fmu has finished generating.
        :return: (int) status code of request, 201 if success
        """
        idf_file = open(self._idf_path, 'rb')
        epw_file = open(self._epw_path, 'rb')

        file = {'idf_file': ('update.idf', idf_file),
                'epw_file': ('update.epw', epw_file)}

        resp = requests.post(init_url, headers=self._header, data=self._init_data, files=file)

        idf_file.close()
        epw_file.close()
        return resp.status_code

    def send_and_init(self):
        """
        send data and initialize model as a simulation object, returns when simulation object has finished initializing
        :return: (int) status code of request, 200 if success
        """
        resp = requests.post(send_fmu, headers=self._header, json=self._init_data)

        # graphql query for all models in db related to initial_model_name.
        model_query = """
                       {{
                          fmuModels(modelN: "{0}"){{
                             modelName
                          }}
                       }}
                       """.format(self._model_name)

        r = requests.get(url=graphql_url, json={'query': model_query}).json()['data']['fmuModels']

        # TODO check if model count = initialized_model_count and relay to user,
        #  account for case when initialized_model_count < model count
        # initialized_model_count = len(r)
        # prints init_data on successful post
        return resp.status_code

    # TODO split into multiple methods giving the user more control over simulations
    def simulate_models(self):
        """
        Starts communication with simulation model and returns when model has reached its final time
        :return: (int) 200 for success
        """
        def test_method(query, url):
            resp = requests.get(url=url, json={'query': query})
            json_data = resp.json()['data']['outputs']
            # self.logger.info("Output current length: {}".format(len(json_data)))
            return len(json_data)

        # TODO needs rework asap
        # query for all models in db related to initial_model_name.
        model_query = """
                   {{
                       fmuModels(modelN: "{0}"){{
                            modelName
                        }}
                   }}
                   """.format(self._model_name)

        r = requests.get(url=graphql_url, json={'query': model_query})

        i = 0

        while i < self._model_count:
            name = r.json()['data']['fmuModels'][i]['modelName']  # extract model name from graphql query response
            print(name)
            self.sim_names.append(name)  # store extracted model names.
            i += 1

        f_time = 60 * 60 * self._final_time

        data_frames = []
        for file in self._csv:
            data_frames.append(pd.read_csv(file))

        i = 0  # first step
        while i < f_time:

            j = 0
            # TODO process models async client side!
            while j < self._model_count:
                # TODO store dataframe in generator method and call next each iter
                if len(data_frames) > 1:
                    df = data_frames[j]
                else:
                    df = data_frames[0]

                row = df.loc[df['time_step'] == i]
                input_dict = row.to_dict('records')
                input_dict = input_dict[0]
                input_data = {
                    'fmu_model': self.sim_names[j],
                    'time_step': i,
                    'input_json': json.dumps(input_dict)
                }

                r = requests.post(input_url, headers=self._header, data=input_data)
                print(r.text + ' ' + str(r.status_code))

                j += 1

            output_query = """
            {{
                outputs(modelN: "{0}", tStep: {1}) {{
                    outputJson
                }}
            }}
            """.format(self._model_name, i)

            try:
                polling2.poll(
                    lambda: test_method(query=output_query, url=graphql_url) == self._model_count,
                    step=0.1,
                    timeout=60)
            except polling2.TimeoutException:
                print("Timeout error occurred\nLength of results is: {}".format(
                    test_method(query=output_query, url=graphql_url)))

            i += self._step_size
        print("\nAll data sent to simulation\n")
        return 200

    def request_model_outputs(self, sim_name):
        f_time = 60*60*self._final_time
        num_of_steps = f_time/self._step_size
        self.logger.info("Expected number of steps: {}".format(num_of_steps))

        def test_method(query, url):
            resp = requests.get(url=url, json={'query': query})
            json_data = resp.json()['data']['outputs']
            self.logger.info("Output current length: {}".format(len(json_data)))
            return len(json_data)

        output_query = """
                        {{
                            outputs(modelN: "{0}") {{
                                timeStep
                                outputJson
                            }}
                        }}
                        """.format(sim_name)

        print("Processing remaining inputs...")
        try:
            polling2.poll(
                lambda: test_method(query=output_query, url=graphql_url) == num_of_steps,
                step=0.1,
                poll_forever=True)
        except polling2.TimeoutException:
            print("Timeout error occurred\nLength of results is: {}".format(test_method(query=output_query, url=graphql_url)))

        json_output = requests.get(url=graphql_url, json={'query': output_query}).json()['data']['outputs']

        # TODO store list of output names and use as csv column
        print("Retrieving outputs...")
        try:
            csv_columns = ['time_step', 'output']
            with open(f'output_csv/{sim_name}.csv', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for out in json_output:
                    writer.writerow({'time_step': out['timeStep'], 'output': json.loads(out['outputJson'])})
        except IOError:
            print("I/O error")

    @staticmethod
    def multi_thread_client(self):
        """
        Let user make multi-threaded requests, simulations per thread = (number of sims / available threads).
        Avoid sequential processing of container requests client side.
        :return:
        """
        return NotImplementedError
