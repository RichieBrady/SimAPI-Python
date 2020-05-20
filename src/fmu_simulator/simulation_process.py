import json
import subprocess
import time
from json import JSONDecodeError

import requests
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from simulator.simulation_obj import SimulationObject


def isint(value):
    try:
        time_step = int(value)
        return time_step
    except ValueError:
        return False


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.fmu", "*.txt"]

    sim_obj = None
    model_name = None
    header = None
    current_time_step = None
    current_input = None
    model_params_set = False
    first_input_set = False
    step_size = None
    prev_time_step = 0

    # when fmu file is saved initialize the pyFMI object
    def on_created(self, event):
        if self.model_params_set is False:
            folder_path = str(event.src_path).rsplit('/', 1)[0]
            with open(folder_path + '/model_params.json') as json_file:
                model_params_ready = False

                try:
                    data = json.load(json_file)
                    print("DATA IN SIM PROC: " + str(data))
                    model_params_ready = True
                except JSONDecodeError:
                    json_file.close()
                    print("model_params.json not ready!")

                if model_params_ready:
                    params = data['model_params'][-1]
                    self.model_name = params['model_name']
                    self.step_size = params['step_size']
                    final_time = params['final_time']
                    fmu_path = '/home/deb/code/fmu_data/{0}/{0}.fmu'.format(self.model_name)

                    self.header = {'Authorization': 'Token ' + params['Authorization']}

                    # if the simulation container is not designated as the first conatainer in a swarm
                    if not params['isSimOne']:
                        # create a new model instance in the django database for this container
                        init_url = 'http://web:8000/init_model/'
                        hostname = subprocess.getoutput("cat /etc/hostname")
                        self.model_name = self.model_name + '_' + hostname

                        init_data = {
                            'model_name': self.model_name,  # change name each time script is run!
                            'step_size': self.step_size,  # step size in seconds. 600 secs = 10 mins
                            'final_time': final_time,  # 24 hours = 86400 secs
                            'container_id': hostname
                        }

                        requests.post(init_url, headers=self.header, data=init_data)

                    self.sim_obj = SimulationObject(model_name=self.model_name, step_size=int(self.step_size),
                                                    final_time=float(final_time),
                                                    path_to_fmu=fmu_path)

                    self.sim_obj.model_init()

                    self.model_params_set = True

    def on_modified(self, event):
        # simulation time steps run here when time_step.txt is updated
        if event.src_path.endswith('time_step.txt') and self.model_params_set is True:
            # read time step value from txt file
            with open(str(event.src_path)) as text_file:

                text_file.seek(0)

                data = text_file.readline()

                self.current_time_step = isint(data)
                print("Current time Step read from file: " + str(self.current_time_step))

            # overly complicated conditional accounts for the case where the process is triggered out of turn
            if self.current_time_step == self.prev_time_step + int(self.step_size) or not self.first_input_set:
                self.first_input_set = True
                self.prev_time_step = self.current_time_step

                graphql_url = 'http://web:8000/graphql/'
                # graphql query to retrieve the input data for the given time step
                input_query = """
                {{
                    inputs(modelN: "{0}", tStep: {1}) {{
                        inputJson
                    }}
                }}
                """.format(str(self.model_name), self.current_time_step)

                r = requests.get(url=graphql_url, json={'query': input_query})

                graphql_response = r.json()['data']['inputs'][0]['inputJson']

                # format response json
                self.current_input = json.loads(json.loads(graphql_response))

                print("\ninput: " + str(self.current_input))

                # run do_step for current time step with current inputs
                output_json = self.sim_obj.do_time_step(self.current_input)

                output_url = 'http://router:8000/route_output/'

                output_json['Authorization'] = self.header['Authorization']
                r = requests.post(output_url, headers=self.header, json=json.dumps(output_json))

                # when last time step has completed free and terminate instance
                if self.current_time_step == self.sim_obj.final_time - int(self.step_size):
                    self.sim_obj.model.free_instance()


if __name__ == '__main__':
    path = '/home/deb/code/fmu_data'
    observer = Observer()
    observer.schedule(MyHandler(), path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
