import requests

from setup import Setup


class Controller:
    setup_user = Setup()

    initialized_model_count = 0

    def send_and_generate(self, initial_model_name, model_count, step_size, final_time, idf_path, epw_path):
        resp = self.setup_user.create_user()

        print(resp.text + ' ' + str(resp.status_code))

        header = self.setup_user.login()

        idf_file = open(idf_path, 'rb')
        epw_file = open(epw_path, 'rb')

        # place .idf and .epw in simapi-python/test_setup_files/  replace a.idf and a.epw
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

    def send_and_init(self, initial_model_name, model_count, step_size, final_time,):
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

